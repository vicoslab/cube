from opengl_gui.gui_components import Gui, Element

def depends_on(self, element) -> None:
    self.parent = element    
    element.dependent_components.append(self)

class ExtendedGui(Gui):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.interaction_context = []
        old_init = Element.__init__
        def new_init(self, **kwargs):
            old_init(self, **kwargs)
            self.parent = None
        Element.__init__ = new_init
        Element.depends_on = depends_on

    def release_interaction_context(self, element):
        if element in self.interaction_context:
            self.interaction_context.remove(element)

    def grab_interaction_context(self, element):
        if self.interaction_context_free(element) and element not in self.interaction_context:
            self.interaction_context.append(element)

    def interaction_context_free(self, element):
        '''
        The main thing we override is how interaction context is taken (and shared).
        If an element grabs the interaction context, it will:
            - share it with its decendants
            - prevent non-decendant elements located in it from having it
        '''
        if len(self.interaction_context) == 0:
            return True
            
        el = element
        for i in range(1, len(self.interaction_context)+1):
            holder = self.interaction_context[-i]
            if holder.is_inside(*el.top) and holder.is_inside(*el.bot):
                while el != None:
                    if el == holder:
                        return True
                    el = el.parent
                return False
        return False
