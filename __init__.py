from .nodes import LoadRawImage, LoadRawImageAdvanced, NODE_DISPLAY_NAME_MAPPINGS

# V1 Legacy Mappings
NODE_CLASS_MAPPINGS = {
    "Load Raw Image": LoadRawImage,
    "Load Raw Image Advanced": LoadRawImageAdvanced,
}
WEB_DIRECTORY = "./web"


# V3 Entrypoint
class RAWExtension:
    @classmethod
    def get_node_list(cls):
        return [LoadRawImage, LoadRawImageAdvanced]


def comfy_entrypoint():
    return RAWExtension


__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    "WEB_DIRECTORY",
    "comfy_entrypoint",
]
