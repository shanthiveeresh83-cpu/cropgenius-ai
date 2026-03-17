import sys
print("Python:", sys.executable)
try:
    import flask
    print("Flask: INSTALLED")
except:
    print("Flask: NOT FOUND")
    print("\nInstall with:")
    print(f'"{sys.executable}" -m pip install flask flask-cors flask-jwt-extended flask-bcrypt python-dotenv')
