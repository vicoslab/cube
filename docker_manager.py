import echolib

import docker
import time

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

        self.command     = None
        self.command_lock = Lock()
        self.stop        = False

        self.pyecho_loop.wait(10)
        
        self.running_containers = dict()

        self.docker_ready      = echolib.Publisher(self.pyecho_client, "containerReady", "int")

    def process(self):

        #start = time.time()

        while not self.stop:

            command = None

            self.command_lock.acquire()
            if self.command is not None:
                command = self.command.split(" ")
                self.command = None
            self.command_lock.release()

            if command is not None:
                
                if command[0] == "1":   # Run container
                    print("Run container with id {}".format(command[1]))
                    
                    if command[1] in self.running_containers:
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
                                        remove=False, detach=True,\
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
                if do_pause:
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

    def __handle_container(self, tag):
        
        if self.active_container[0] != tag:
            self.stop_active_container()

            return True

        return False

    def __callback(self, message):

        self.command_lock.acquire()
        self.command = echolib.MessageReader(message).readString()
        print("Got command: {}".format(self.command))
        self.command_lock.release()

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

    dm.stop_active_container()
    

if __name__ == '__main__':
    main()
