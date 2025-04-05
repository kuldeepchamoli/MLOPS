###building url dynaMICALLY
###variable rule
###jinja 2template engine
'''
{{ }} expressionsto print output in html
{%..%} conditions loops
{#..#} for comments
'''

from flask import Flask,render_template,request,redirect,url_for # type: ignore
'''science
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


##variable rule
@app.route('/success/<int:score>')
def success(score):
    res=""
    if score>=50:
        res="Pass"
    else:
        res="Fail"

    return render_template('result.html',results=res)

##variable rule
@app.route('/successif/<int:score>')
def success_if(score):
    
    return render_template('result.html',results=score)

###if condition
@app.route('/successres/<int:score>')
def success_result(score):
    res=""
    if score>=50:
        res="Pass"
    else:
        res="Fail"
    exp={'score':score,"res":res}
    return render_template('result1.html',results=exp)

@app.route('/getresult', methods=['GET', 'POST'])
def submit():
    try:
        if request.method == 'POST':
            science = float(request.form.get('science', 0))  
            maths = float(request.form.get('maths', 0))
            c = float(request.form.get('c', 0))
            data_science = float(request.form.get('data_science', 0))

            total_score = (science + maths + c + data_science) / 4.0

            return redirect(url_for('success_result', score=int(total_score)))
        
        # Handle GET request - Render the form page
        return render_template("getresult.html")  

    except ValueError:
        return "Invalid input! Please enter numeric values only.", 400

@app.route('/fail/<int:score>')
def fail(score):
    return render_template('result.html',results=score)

if __name__=="__main__":
    app.run(debug=True)