{ pkgs, ... }: {
  # Which nixpkgs channel to use.
  channel = "stable-24.05"; # or "unstable"
  # Use https://search.nixos.org/packages to find packages
  packages = [
    pkgs.python3
    pkgs.python311Packages.pip
    pkgs.python311Packages.fastapi
    pkgs.python311Packages.uvicorn
    pkgs.imagemagick
    pkgs.rclone
  ];
  # Sets environment variables in the workspace
  env = {};
  idx = {
    previews = {
      enable = true;
      previews = {
        web = {
          command = [ "./webui.sh" ];
          env = { PORT = "8080"; };
          manager = "web";
        };
      };
    };
    # Search for the extensions you want on https://open-vsx.org/ and use "publisher.id"
    extensions = [ "ms-python.python" "humao.rest-client" "Google.geminicodeassist"];
    workspace = {
      # Runs when a workspace is first created with this `dev.nix` file
      onCreate = {
        install =
          "python -m venv .venv && source .venv/bin/activate &&  pip install -r requirements.txt";
        # Open editors for the following files by default, if they exist:
        default.openFiles = [ "app.py" ];
      };
    };
  };
}