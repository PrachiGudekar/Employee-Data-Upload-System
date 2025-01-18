from app import db

class Employee(db.Model):
    __tablename__ = 'employee'  # Optional: Specify the table name explicitly

    employee_id = db.Column(db.String(50), primary_key=True, unique=True, nullable=False)
    employee_name = db.Column(db.String(100), nullable=False)  # Set nullable=False if it's mandatory
    date_of_joining = db.Column(db.Date, nullable=False)  # Ensure date is provided
    date_of_birth = db.Column(db.Date, nullable=False)
    department = db.Column(db.String(100), nullable=False)  # Set nullable=False if mandatory
    reporting_authority_id = db.Column(db.String(50), nullable=True)  # Nullable if it's optional
    mobile_number = db.Column(db.String(20), nullable=False)  # Ensure mobile number is provided
    email_id = db.Column(db.String(100), nullable=False, unique=True)  # Ensure unique emails
    pan_number = db.Column(db.String(50), nullable=False, unique=True)  # Ensure unique PAN numbers
    fixed_salary = db.Column(db.Float, nullable=False)  # Ensure salary fields are provided
    bonus_salary = db.Column(db.Float, nullable=False)
    total_salary = db.Column(db.Float, nullable=False)
    designation = db.Column(db.String(100), nullable=True)  # Nullable if not always provided

    def __repr__(self):
        return f'<Employee {self.employee_id}>'
