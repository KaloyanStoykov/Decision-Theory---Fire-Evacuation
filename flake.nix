{
  description = "Gymnasium LunarLander environment on Hyprland (Wayland)";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          config.allowUnfree = true;
        };
        pythonEnv = pkgs.python3.withPackages
          (ps: with ps; [ gymnasium pygame matplotlib numpy ]);
      in {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            pythonEnv
            pkgs.xorg.libX11
            pkgs.SDL2
            pkgs.python312Packages.pybox2d
          ];

          shellHook = ''
            export SDL_VIDEODRIVER=wayland
            echo "SDL_VIDEODRIVER set to way for Gym UI on Hyprland."
            fish; exit
          '';
        };
      });
}
