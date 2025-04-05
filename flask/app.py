from flask import Flask,render_template,request # type: ignore
'''
craetes instance offlask class which will be ur wsgi applicaton
'''

###WSGI application
app=Flask(__name__)

@app.route("/index")###decorator
def welcome():
    return render_template('index.html')
    
@app.route("/")###decorator
def index():
    return "This is main"

@app.route("/about")   
def about():
    return render_template('aboutUs.html')

@app.route('/form',methods=['GET','POST'])
def form():
    if request.method=='POST':
        name=request.form['name']
        return f'Hello {name}!'
    return render_template('form.html')

@app.route('/submit',methods=['GET','POST'])
def submit():
    if request.method=='POST':
        name=request.form['name']
        return f'Hello {name}!'
    return render_template('form.html')


if __name__=="__main__":
    app.run(debug=True)