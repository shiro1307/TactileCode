{ pkgs }: {
    deps = [
        pkgs.python312
        pkgs.nodejs_20
        pkgs.git
    ];
    env = {
        PYTHON_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
            pkgs.libc
        ];
        LANG = "en_US.UTF-8";
    };
}
