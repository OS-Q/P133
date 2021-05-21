from platformio.managers.platform import PlatformBase


class P133Platform(PlatformBase):

    def configure_default_packages(self, variables, targets):
        if "arduino" in variables.get("pioframework", []):
            self.packages["toolchain-sdcc"]["version"] = "~1.30901.0"
        return PlatformBase.configure_default_packages(self, variables, targets)

    def get_boards(self, id_=None):
        result = PlatformBase.get_boards(self, id_)
        if not result:
            return result
        if id_:
            return self._add_default_debug_tools(result)
        else:
            for key, value in result.items():
                result[key] = self._add_default_debug_tools(result[key])
        return result

    def _add_default_debug_tools(self, board):
        debug = board.manifest.get("debug", {})
        upload_protocols = board.manifest.get("upload", {}).get(
            "protocols", [])
        if "tools" not in debug:
            debug["tools"] = {}

        for link in ("stlink",):
            if link == "stlink":
                server_args = ["-s", "$PACKAGE_DIR/scripts"]
                if debug.get("openocd_board"):
                    server_args.extend([
                        "-f", "board/%s.cfg" % debug.get("openocd_board")
                    ])
                else:
                    assert debug.get("openocd_target"), (
                        "Missing target configuration for %s" % board.id)
                    server_args.extend([
                        "-f", "interface/stlink-dap.cfg",
                        # transport protocol swim is automatically selected, no need to set it
                        "-f", "target/%s.cfg" % debug.get("openocd_target")
                    ])
                    server_args.extend(debug.get("openocd_extra_args", []))

                debug["tools"][link] = {
                    "server": {
                        "package": "tool-openocd",
                        "executable": "bin/openocd",
                        "arguments": server_args
                    }
                }
            debug["tools"][link]["onboard"] = link in debug.get(
                "onboard_tools", [])
            debug["tools"][link]["default"] = link in debug.get(
                "default_tools", [])

        board.manifest["debug"] = debug
        return board
