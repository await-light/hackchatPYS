from flask import Flask,render_template
from multiprocessing import Process

def main(host,port):
	app = Flask(__name__)

	@app.route("/")
	def home():
		return render_template('./index.html')
	
	return Process(target=app.run,args=(host,port,))
