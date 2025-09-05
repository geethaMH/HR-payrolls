from flask import Flask, render_template, request, redirect, url_for
import pymysql

app = Flask(__name__)

# MySQL connection function
def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="1234",  # replace with your MySQL password
        database="employee_management"
    )

# Home page: show employees (filtered for duplicates)
@app.route('/')
def index():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees")
    employees = cursor.fetchall()
    conn.close()

    # Filter duplicates based on (name, age, department, salary)
    unique_employees = []
    seen = set()
    for emp in employees:
        key = (emp[1], emp[2], emp[3], emp[4])  # exclude ID
        if key not in seen:
            unique_employees.append(emp)
            seen.add(key)

    return render_template('index.html', employees=unique_employees)

# Add employee
@app.route('/add', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        department = request.form['department']
        salary = request.form['salary']

        conn = get_connection()
        cursor = conn.cursor()
        # Optional: check if employee already exists
        cursor.execute("SELECT * FROM employees WHERE name=%s AND age=%s AND department=%s AND salary=%s",
                       (name, age, department, salary))
        existing = cursor.fetchone()
        if not existing:
            cursor.execute(
                "INSERT INTO employees (name, age, department, salary) VALUES (%s,%s,%s,%s)",
                (name, age, department, salary)
            )
            conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add.html')

# Update employee
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_employee(id):
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        department = request.form['department']
        salary = request.form['salary']

        cursor.execute(
            "UPDATE employees SET name=%s, age=%s, department=%s, salary=%s WHERE id=%s",
            (name, age, department, salary, id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    else:
        cursor.execute("SELECT * FROM employees WHERE id=%s", (id,))
        employee = cursor.fetchone()
        conn.close()
        return render_template('update.html', employee=employee)

# Delete employee
@app.route('/delete/<int:id>')
def delete_employee(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM employees WHERE id=%s", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Delete all employees
@app.route('/delete_all')
def delete_all():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM employees")
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
