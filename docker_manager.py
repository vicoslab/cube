import echolib

import docker
import time
from load_demos import load_demos

from threading import Thread, Lock

class DockerManager():

    def __init__(self):
        self.active_container = [None, None]
        self.docker          = docker.from_env()

        self.pyecho_loop   = echolib.IOLoop()
        self.pyecho_client = echolib.Client()
        self.pyecho_loop.add_handler(self.pyecho_client)

        self.pyechoDockerIn  = echolib.Subscriber(self.pyecho_client, "dockerIn", "string", self.__callback)
        self.pyecho_docker_out = echolib.Publisher(self.pyecho_client, "dockerOut", "string")
        self.pyecho_docker_stoped = echolib.Publisher(self.pyecho_client, "docker_stoped", "string")

        self.pyecho_docker_channel_out = echolib.Publisher(self.pyecho_client, "docker_demo_command_input", "int")

        self.command     = []
        self.command_lock = Lock()
        self.stop        = False

        self.pyecho_loop.wait(10)

        self.container_vram_usage = {
            demo["dockerId"]: [demo["vramMin"],demo["vramMax"], "nopause" in demo]
            for demo in map(lambda x: x["cfg"], load_demos().values())
        }

        self.vram_max = 16000 # 4060ti 16GB
        self.vram_usage = 1000 # reserve some memory for gui, host applications, etc.
        
        self.running_containers = dict()

        self.docker_ready      = echolib.Publisher(self.pyecho_client, "containerReady", "int")

    def process(self):

        #start = time.time()

        while not self.stop:

            command = None

            self.command_lock.acquire()
            if len(self.command) > 0:
                command = self.command.pop(0).split(" ")
                
                # Skip command pairs if they act on the same container (i.e. add and remove quickly)
                if len(self.command) > 0:
                    next = self.command[0].split(" ")
                    if command[1] == next[1] and \
                        int(command[0]) * int(next[0]) == -1: # This part shouldn't be neccessary, but just in case
                        self.command.pop(0)
                        command = None
            self.command_lock.release()

            if command is not None:
                
                if command[0] == "1":   # Run container
                    print("Run container with id {}".format(command[1]))
                    
                    if command[1] in self.running_containers:
                        self.ensure_vram(command[1])
                        print(f"Container {command[1]} already running ... will unpause it.")
                        # container should already be running - just unpause it
                        if self.running_containers[command[1]] is not None:
                            try:
                                self.running_containers[command[1]].unpause()
                                print(f"Container {command[1]} unpaused.")
                            
                                # time.sleep(1)
                                
                                # manually send signal for container ready since container is already running
                                for i in range(0,10):
                                    self.pyecho_loop.wait(10)
                        
                                    writer = echolib.MessageWriter()
                                    writer.writeInt(1)
                                    self.docker_ready.send(writer)
                                    print(f"Sending docker_ready from docker manager.")

                                start_fresh_container = False
        
                                self.active_container[0] = command[1]
                                self.active_container[1] = self.running_containers[command[1]]

                            except:
                                print("Error unpausing docker container... (removing and starting new)")
                                self.stop_active_container(do_pause=False)
                                start_fresh_container = True 
                           
                    else:
                        start_fresh_container = True
                    
                    if start_fresh_container:                        
                        for image in self.docker.images.list():
                            
                            if len(image.tags) > 0 and image.tags[0] == command[1]:
                                print("Image with matching tag found...")
                                self.ensure_vram(command[1])

                                flag = self.__handle_container(command[1])

                                output_channel = "outContainer" + str(command[0])
                                input_channel  = "inContainer"  + str(command[0])

                                print(f"{output_channel} {input_channel}")

                                w = echolib.MessageWriter()
                                w.writeString(output_channel + " " + input_channel)
                                self.pyecho_docker_out.send(w)
                                
                                if flag:
                                    print("setting self.active_container to ", command[1])
                                    self.active_container[0] = command[1]
                                    self.active_container[1] = self.docker.containers.run(image.id,\
                                        device_requests=[docker.types.DeviceRequest(count=1, driver="nvidia", capabilities=[['gpu']])],\
                                        detach=True,\
                                        volumes = {"/tmp/echo.sock" : {"bind" : "/tmp/echo.sock", "mode" : "rw"}},\
                                        log_config = docker.types.LogConfig(type=docker.types.LogConfig.types.JSON), 
                                        environment=dict(PYTHONUNBUFFERED=1),
                                        network_mode="host")           

                                    self.running_containers[command[1]] = self.active_container[1]


                elif command[0] == "-1": # Stop container
                    print("Stopping contianer {}".format(command[1]))
                    self.stop_active_container()

            time.sleep(0.3)
        
    def stop_active_container(self, do_pause = True):
        print("self.active_container:", self.active_container)
        if self.active_container[0] is not None:
            try:
                vramMin, vramMax, nopause = self.container_vram_usage[self.active_container[0]]
                self.vram_usage -= vramMax
                if do_pause and not nopause:
                    self.vram_usage += vramMin
                    # make sure demo is not processing befor pausing it
                    # the main gui should already be sending this, but this is just in case
                    if self.pyecho_docker_channel_out is not None:
                        writer = echolib.MessageWriter()
                        writer.writeInt(0) # command to disable processing
                        self.pyecho_docker_channel_out.send(writer)

                    time.sleep(0.25)
                    
                    print(f"Pausing active docker.")
                    self.active_container[1].pause()
                else:    
                    print(f"Stoping active docker.")
                    self.active_container[1].stop()
                    self.running_containers.pop(self.active_container[0])

                w = echolib.MessageWriter()
                w.writeString(self.active_container[0])
                self.pyecho_docker_stoped.send(w)

            except:
                print("Error stopping docker container...")

            print("setting self.active_container to None")
            self.active_container[0] = self.active_container[1] = None
    
    
    def stop_all_containers(self):
        for id,container in self.running_containers.items():
            try:
                container.stop()
                vramMin, vramMax, _ = self.container_vram_usage[id]
                if self.active_container[0] == id:
                    self.vram_usage -= vramMax
                    w = echolib.MessageWriter()
                    w.writeString(self.active_container[0])
                    self.pyecho_docker_stoped.send(w)
                else:
                    self.vram_usage -= vramMin
            except:
                print("Error stopping docker container...")

            if self.active_container[0] == id:
                self.active_container[0] = self.active_container[1] = None
        
        self.running_containers = dict()

    def __handle_container(self, tag):
        
        if self.active_container[0] != tag:
            self.stop_active_container()

            return True

        return False

    def __callback(self, message):

        self.command_lock.acquire()
        self.command.append(echolib.MessageReader(message).readString())
        print("Got command: {}".format(self.command))
        self.command_lock.release()
        
    def ensure_vram(self, tag):
        print("ensure vram")
        
        vramMin, vramMax, _ = self.container_vram_usage[tag]
        if tag in self.running_containers:
            vram_needed = self.vram_usage - vramMin + vramMax
        else:
            vram_needed = self.vram_usage + vramMax
        
        print(f"Projected VRAM usage: {vram_needed}/{self.vram_max}")
        while vram_needed > self.vram_max:
            # Always remove container with largest usage first
            freed, tag = max([(self.container_vram_usage[t][0], t) for t in self.running_containers.keys()])
            print(f"Removing {tag} to free {freed} MB")
            self.running_containers.pop(tag).stop()

            w = echolib.MessageWriter()
            w.writeString(tag)
            self.pyecho_docker_stoped.send(w)
            vram_needed -= freed
            print(f"Projected VRAM usage: {vram_needed}/{self.vram_max}")

        self.vram_usage = vram_needed

def main():
    dm = DockerManager()

    th = Thread(target = dm.process)
    th.start()

    print("waiting for pyecho")
    try:
        while dm.pyecho_loop.wait(10):
            time.sleep(0.001)
            
    except KeyboardInterrupt:
        pass

    dm.stop = True
    th.join()

    dm.stop_all_containers()
    

if __name__ == '__main__':
    main()
