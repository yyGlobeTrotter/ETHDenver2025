{ pkgs }: {
  deps = [
    pkgs.python310
    pkgs.python310Packages.pip
    pkgs.python310Packages.flask
    pkgs.python310Packages.flask-cors
    pkgs.python310Packages.requests
    pkgs.python310Packages.numpy
    pkgs.python310Packages.pandas
    pkgs.python310Packages.python-dotenv
    pkgs.python310Packages.gunicorn
  ];
} 