from flask import Flask, render_template, request
import pandas as pd
import pickle
import numpy as np

app = Flask(__name__)

@app.route('/')
@app.route('/home', methods=['POST','GET'])
def home():
    teams = ['Royal Challengers Bangalore', 'Rajasthan Royals',
       'Chennai Super Kings', 'Mumbai Indians', 'Punjab Kings',
       'Kolkata Knight Riders', 'Delhi Capitals', 'Sunrisers Hyderabad']

    logo = ['rcb','rr','csk','mi','pk','kkr','dc','srh']

    
    cities = ['Dharamsala', 'Kolkata', 'Bangalore', 'Jaipur', 'Mumbai',
    'Chandigarh', 'Abu Dhabi', 'Chennai', 'Durban', 'Delhi','Visakhapatnam',
     'Port Elizabeth', 'Hyderabad', 'Pune','Johannesburg', 'Indore',
      'Sharjah', 'Bengaluru', 'Ranchi','Centurion', 'Cape Town', 'Cuttack',
       'Kimberley', 'Ahmedabad','Raipur', 'Mohali', 'East London', 
       'Bloemfontein', 'Nagpur']


    pred = 0
    if request.method == "POST":

        pred = 1

        batting_team = teams[int(request.form['battingteam'])]
        bowling_team = teams[int(request.form['bowlingteam'])]

        if batting_team == 'Punjab Kings':
            batting_team = 'Kings XI Punjab'
        if bowling_team == 'Punjab Kings':
            bowling_team = 'Kings XI Punjab'
        try:
            city = cities[int(request.form['city'])]
            total_runs = int(request.form['target'])
            current_runs = float(request.form['score'])
            runs_left = int(total_runs - current_runs)
            wickets_fall = int(request.form['wickets'])
        except :
            pred = 2
            error = "Invalid Data Entered"
            return render_template('home.html', teams=teams, city=cities, pred=pred,error =error)
        x = float(request.form['overs'])
        y = int(x)
        z = (x - y)*10
        ball = y*6+int(z)
    
        ball_left = int(120 - ball)
        
        try:
            crr = round(current_runs*6/ball,2)
            rrr = round(runs_left*6/ball_left,2)
        except :
            pred = 2
            error = "Over Can Not Be Zero"
            return render_template('home.html', teams=teams, city=cities, pred=pred,error =error)
        
        logo1 = logo[int(request.form['battingteam'])]
        logo2 = logo[int(request.form['bowlingteam'])]

        df = pd.DataFrame({'batting_team':[batting_team], 'bowling_team':[bowling_team], 'city':[city], 'runs_left':[runs_left],
                   'balls_left':[ball_left],'wickets':[wickets_fall], 'total_runs_x':[total_runs], 'crr':[crr], 'rrr':[rrr]})


        model = pickle.load(open('model/pipe.pkl','rb'))

        if model.classes_[0]==0:
            loss = float(model.predict_proba(df)[:,0])
        if model.classes_[1]==0:
            loss = float(model.predict_proba(df)[:,1])

        loss = float(round(loss*100,2))
        if wickets_fall<6 and loss>75 and (rrr-crr)<=4 and ball<=80:
           
            loss = loss-30

        if wickets_fall<=4 and loss>65 and (rrr-crr)<=5.5 and ball<=90:
            
            loss = loss-35

        if wickets_fall<8 and loss>80 and (rrr-crr)<=5 and ball_left>=96 and ball_left<120:
            
            loss = loss-35

        if wickets_fall>=6 and loss<60 and rrr>14 and ball_left<30:
            loss = loss+20
            
        if loss>50 and rrr<12 and ball_left<=36:
            loss = loss-20

        loss = round(loss,2)
        win = round(100-loss,2)
      
        if win>loss:
            song = logo[int(request.form['battingteam'])]
        if loss>win:
            song = logo[int(request.form['bowlingteam'])]

  
        if current_runs>total_runs:
            pred = 2
            error = "Current Runs Can Not Be Greater Than Target"
            return render_template('home.html', teams=teams, city=cities, pred=pred,error =error)

        if wickets_fall>10 or wickets_fall<0:
            pred = 2
            error = "Wickets Must Be Between 1-10"
            return render_template('home.html', teams=teams, city=cities, pred=pred,error =error)

        if ball/6>20 or ball/6<0:
            pred = 2
            error = "Overs Must Be Between 1-20"
            return render_template('home.html', teams=teams, city=cities, pred=pred,error =error)

        if batting_team==bowling_team:
            pred = 2
            error = "Batting Team And Bowling Team Must Be Different"
            return render_template('home.html', teams=teams, city=cities, pred=pred,error =error)

        bteam = logo1.upper() 

        return render_template('home.html', teams=teams, city=cities, pred=pred, loss=loss, win=win, logo1=logo1,logo2=logo2,song=song,crr=crr,rrr=rrr,bteam=bteam,target=total_runs,runs_left=runs_left,ball_left=ball_left,wickets_fall=wickets_fall,current_score=int(current_runs),overs=x)

    return render_template('home.html', teams=teams, city=cities)

if __name__ == '__main__':
    app.run(debug=False)
