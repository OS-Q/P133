import os
import sys

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()
platform = env.PioPlatform()
board_config = env.BoardConfig()

FRAMEWORK_DIR = platform.get_package_dir("A133")
assert os.path.isdir(FRAMEWORK_DIR)


def inject_dummy_reference_to_main():
    build_dir = env.subst("$BUILD_DIR")
    dummy_file = os.path.join(build_dir, "_pio_main_ref.c")
    if not os.path.isfile(dummy_file):
        if not os.path.isdir(build_dir):
            os.makedirs(build_dir)
        with open(dummy_file, "w") as fp:
            fp.write("void main(void);void (*dummy_variable) () = main;")

    env.Append(PIOBUILDFILES=dummy_file)


env.Append(
    CCFLAGS=[
        "--less-pedantic"
    ],

    CPPDEFINES=[
        "ARDUINO_ARCH_STM8",
        ("ARDUINO", 10802),
        ("double", "float"),
        "USE_STDINT",
        "__PROG_TYPES_COMPAT__"
    ],

    CPPPATH=[
        os.path.join(FRAMEWORK_DIR, "cores", env.BoardConfig().get("build.core")),
        os.path.join(FRAMEWORK_DIR, "STM8S_StdPeriph_Driver", "inc")
    ],

    LIBPATH=[
        os.path.join(FRAMEWORK_DIR, "STM8S_StdPeriph_Driver", "lib")
    ],

    LIBS=[board_config.get("build.mcu")[0:8].upper()],

    LIBSOURCE_DIRS=[
        os.path.join(FRAMEWORK_DIR, "libraries")
    ]
)

inject_dummy_reference_to_main()

# By default PlatformIO generates "main.cpp" for the Arduino framework.
# But Sduino doesn't support C++ sources. Exit if a file with a C++
# extension is detected.
for root, _, files in os.walk(env.subst("$PROJECT_SRC_DIR")):
    for f in files:
        if f.endswith((".cpp", ".cxx", ".cc")):
            sys.stderr.write(
                "Error: Detected C++ file `%s` which is not compatible with Arduino"
                " framework as only C/ASM sources are allowed.\n"
                % os.path.join(root, f)
            )
            env.Exit(1)

#
# Target: Build Core Library
#

libs = []

if "build.variant" in env.BoardConfig():
    env.Append(
        CPPPATH=[
            os.path.join(
                FRAMEWORK_DIR, "variants", env.BoardConfig().get("build.variant"))
        ]
    )
    libs.append(env.BuildLibrary(
        os.path.join("$BUILD_DIR", "FrameworkArduinoVariant"),
        os.path.join(FRAMEWORK_DIR, "variants", env.BoardConfig().get("build.variant"))
    ))

libs.append(env.BuildLibrary(
    os.path.join("$BUILD_DIR", "FrameworkArduino"),
    os.path.join(FRAMEWORK_DIR, "cores", env.BoardConfig().get("build.core"))
))

env.Prepend(LIBS=libs)
