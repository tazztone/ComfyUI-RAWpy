from comfy_api.latest import ComfyExtension, io
from .nodes import LoadRawImage, LoadRawImageAdvanced

# V1 Legacy Mappings - Keeping for backward compatibility if needed,
# but V3 should take precedence.
NODE_CLASS_MAPPINGS = {
    "Load Raw Image": LoadRawImage,
    "Load Raw Image Advanced": LoadRawImageAdvanced,
}
WEB_DIRECTORY = "./web"


# V3 Entrypoint
class RAWExtension(ComfyExtension):
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return [LoadRawImage, LoadRawImageAdvanced]


async def comfy_entrypoint() -> ComfyExtension:
    return RAWExtension()


__all__ = [
    "NODE_CLASS_MAPPINGS",
    "WEB_DIRECTORY",
    "comfy_entrypoint",
]
