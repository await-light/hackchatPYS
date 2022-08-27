from flask import Flask,render_template
from multiprocessing import Process

def main(host,port):
	app = Flask(__name__)

	@app.route("/")
	def home():
		return render_template('./index.html')

	app.run(host,port,debug=True)
	
if __name__ == '__main__':
	main("0.0.0.0",6059)