{
    description = "";
    inputs.nixpkgs.url = "github:NixOS/nixpkgs";
    inputs.flake-utils.url = "github:numtide/flake-utils";
    outputs = {self, nixpkgs, flake-utils}:
        flake-utils.lib.eachDefaultSystem(system:
        let pkgs = nixpkgs.legacyPackages.${system}; in {
            devShells.default = (pkgs.poetry2nix.mkPoetryEnv {
                projectDir = ./.;
                editablePackageSources = {
                    nomsable = ./.;
                };
                overrides = pkgs.poetry2nix.defaultPoetryOverrides.extend (self: super: {
                    django-libsass = super.django-libsass.overridePythonAttrs (old: {
                        buildInputs = (old.buildInputs or []) ++ [super.setuptools];
                    });
                    filelock = super.filelock.overridePythonAttrs (old: {
                        buildInputs = (old.buildInputs or []) ++ [super.hatchling super.setuptools-scm super.hatch-vcs];
                    });
                });
            }).env;
        });
}
