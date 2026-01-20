from .nodes import LoadRawImage, NODE_DISPLAY_NAME_MAPPINGS

# V1 Legacy Mappings
NODE_CLASS_MAPPINGS = {"Load Raw Image": LoadRawImage}
WEB_DIRECTORY = "./web"


# V3 Entrypoint
class RAWExtension:
    @classmethod
    def get_node_list(cls):
        return [LoadRawImage]


def comfy_entrypoint():
    return RAWExtension


__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    "WEB_DIRECTORY",
    "comfy_entrypoint",
]
