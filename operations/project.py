
import gitlab

class ProjectOp():
    def __init__(self, glapi):
        self.glapi = glapi

    def run (self, saeProjectName):
        glapi = self.glapi

        glapi.create_get_group(saeProjectName)

