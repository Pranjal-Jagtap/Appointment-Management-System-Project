from flask  import Flask,request,render_template,session,url_for,redirect,flash,get_flashed_messages
from psycopg.errors import UniqueViolation
from datetime import date 
import psycopg
conn=psycopg.connect(host="localhost",dbname="appointment_db",user="postgres",port=5432,password="act")
print("postgres connected successfullly")
app=Flask(__name__)
app.secret_key="appointment_secret_key"
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/Register",methods=["GET","POST"])
def Register():
    if request.method=="POST":
        name=request.form.get("name")
        email=request.form.get("email")
        password=request.form.get("password")
        try:
            cur=conn.cursor()
            cur.execute("""insert into users (name,email,password) values( %s, %s ,%s)""",(name,email,password))
            conn.commit()
            cur.close()
            flash("Registration successful!","success")
            return redirect (url_for("Register"))
        except UniqueViolation:
            conn.rollback()
            flash("Email already exist","error")

        except Exception as e:
            conn.rollback()
            print("database error ",e)
            flash("Registration failed. please try again","error")
            return redirect(url_for("Register"))
        
    return render_template("Register.html")

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        email=request.form.get("email")
        password=request.form.get("password")
        cur=conn.cursor()
        cur.execute("select * from users where email=%s AND password=%s",(email,password))
        user=cur.fetchone()
        cur.close()
        if user:
            session["user_id"]=user[0]
            return redirect(url_for("dashboard"))
        else:
            flash(" invalid email or password ","error")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    conn=psycopg.connect(host="localhost",dbname="appointment_db",user="postgres",port=5432,password="act")   
    cur=conn.cursor()

    user_id=session["user_id"]
    cur.execute("select count(*) from appointments where user_id=%s",(user_id,))
    total=cur.fetchone()[0]

    cur.execute("select count(*) from appointments where user_id=%s and appointment_date>=current_date and status='booked'",(user_id,))
    upcoming=cur.fetchone()[0]

    cur.execute("select count(*) from appointments where user_id=%s and status='cancelled'",(user_id,))
    cancelled=cur.fetchone()[0]

    cur.close()
    conn.close()

    
    return render_template("dashboard.html",total=total,upcoming=upcoming,cancelled=cancelled)
    
@app.route("/book",methods=["GET","POST"])
def book():
    if "user_id" not in session:
        flash(" please login first" ,"error")
    if request.method=="POST":
        appointment_date=request.form.get("appointment_date")
        appointment_time=request.form.get("appointment_time")
        reason=request.form.get("reason")
        user_id=session["user_id"]
        cur=conn.cursor()
        cur.execute("select id from appointments where appointment_date=%s and appointment_time=%s and status='booked'",(appointment_date,appointment_time))
        existing=cur.fetchone()

        if existing:
            flash("This time slot is already booked !","error")
            return redirect(url_for("book"))
        cur.execute("insert into appointments (user_id,appointment_date,appointment_time,reason) values (%s,%s,%s,%s)",(user_id,appointment_date,appointment_time,reason))
        conn.commit()
        cur.close()
        flash ("Appointment booked successfully","success")
        return redirect(url_for("appointments"))
    return render_template("book.html",today=date.today().isoformat())
@app.route("/appointments")
def appointments():
    if "user_id" not in session:
        flash( "please login first","error")
        return redirect(url_for("login"))
    conn=psycopg.connect(host="localhost",dbname="appointment_db",user="postgres",port=5432,password="act")   
    cur=conn.cursor()
    user_id=session ["user_id"]
    cur.execute("select id,appointment_date,appointment_time,reason,status from appointments where  user_id=%s order by appointment_date,appointment_time",(user_id,))
    appointments=cur.fetchall()
    cur.close()
    return render_template("appointments.html",appointments=appointments)

@app.route("/update/<int:appointment_id>",methods=["GET","POST"])
def update_appointment(appointment_id):
     if "user_id" not in session:
        return redirect(url_for("login"))
     conn=psycopg.connect(host="localhost",dbname="appointment_db",user="postgres",port=5432,password="act")
     cur=conn.cursor()
     if request.method=="POST":
         appointment_date=request.form.get("appointment_date")
         appointment_time=request.form.get("appointment_time")
         reason=request.form.get("reason")
         cur.execute("update appointments set appointment_date=%s ,appointment_time =%s  ,reason =%s where id=%s and user_id=%s",(appointment_date,appointment_time,reason,appointment_id,session["user_id"]))
         conn.commit()
         cur.close()
         conn.close()
         return redirect(url_for("appointments"))
     cur.execute("select id,appointment_date,appointment_time,reason from appointments where id=%s and user_id=%s",(appointment_id,session["user_id"]))
     appointment=cur.fetchone()
     cur.close()
     conn.close()
     if appointment is None:
         return redirect(url_for("appointments"))
        
     return render_template("update_appointment.html",appointment=appointment,today=date.today().isoformat())


@app.route("/cancel/<int:appointment_id>",methods=["POST"])
def cancel_appointment(appointment_id):
    if 'user_id' not in session:
        flash ("please login first","error")
        return redirect(url_for("login"))
    conn=psycopg.connect(host="localhost",dbname="appointment_db",user="postgres",port=5432,password="act")
    cur=conn.cursor()
    cur.execute("update appointments set status='cancelled' where id=%s and user_id=%s",(appointment_id,session["user_id"]))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("appointments"))
 
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))
if __name__=="__main__":
    app.run(debug=True)  



    

