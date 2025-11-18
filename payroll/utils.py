import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from decimal import Decimal
from django.core.files.base import ContentFile
from django.utils import timezone
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import os

from .models import PayrollUpload, Employee, SalaryComponent, PayrollReport


class ExcelProcessor:
    """Class to handle Excel file processing"""
    
    # Expected column names (case-insensitive)
    EXPECTED_COLUMNS = [
        'employee_id', 'name', 'email', 'department', 'designation',
        'basic_pay', 'hra', 'variable_pay', 'special_allowance', 'other_allowances'
    ]
    
    def __init__(self, file_path, upload_instance):
        self.file_path = file_path
        self.upload_instance = upload_instance
        self.errors = []
        self.warnings = []
    
    def validate_file(self):
        """Validate Excel file structure"""
        try:
            workbook = openpyxl.load_workbook(self.file_path)
            sheet = workbook.active
            
            # Check if file is empty
            if sheet.max_row < 2:
                self.errors.append("Excel file is empty or has no data rows")
                return False
            
            # Get header row
            headers = [cell.value for cell in sheet[1]]
            headers = [str(h).strip().lower().replace(' ', '_') if h else '' for h in headers]
            
            # Check for required columns
            missing_columns = []
            for col in self.EXPECTED_COLUMNS:
                if col not in headers:
                    missing_columns.append(col)
            
            if missing_columns:
                self.errors.append(f"Missing required columns: {', '.join(missing_columns)}")
                return False
            
            # Check row limit
            if sheet.max_row > 101:  # 1 header + 100 data rows
                self.errors.append("Excel file contains more than 100 employees. Maximum limit is 100.")
                return False
            
            return True
            
        except Exception as e:
            self.errors.append(f"Error reading Excel file: {str(e)}")
            return False
    
    def parse_and_save(self):
        """Parse Excel file and save to database"""
        try:
            workbook = openpyxl.load_workbook(self.file_path)
            sheet = workbook.active
            
            # Get headers
            headers = [cell.value for cell in sheet[1]]
            headers = [str(h).strip().lower().replace(' ', '_') if h else '' for h in headers]
            
            # Create column mapping
            col_map = {header: idx for idx, header in enumerate(headers)}
            
            employees_created = 0
            
            # Process each row
            for row_idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
                try:
                    # Extract employee data
                    employee_id = str(row[col_map['employee_id']]).strip() if row[col_map['employee_id']] else None
                    name = str(row[col_map['name']]).strip() if row[col_map['name']] else None
                    
                    # Skip empty rows
                    if not employee_id or not name:
                        self.warnings.append(f"Row {row_idx}: Skipped empty row")
                        continue
                    
                    email = str(row[col_map['email']]).strip() if row[col_map.get('email')] and row[col_map.get('email')] else None
                    department = str(row[col_map['department']]).strip() if row[col_map.get('department')] and row[col_map.get('department')] else None
                    designation = str(row[col_map['designation']]).strip() if row[col_map.get('designation')] and row[col_map.get('designation')] else None
                    
                    # Create employee
                    employee = Employee.objects.create(
                        upload=self.upload_instance,
                        employee_id=employee_id,
                        name=name,
                        email=email,
                        department=department,
                        designation=designation
                    )
                    
                    # Extract salary components
                    def get_decimal_value(value):
                        if value is None or value == '':
                            return Decimal('0.00')
                        try:
                            return Decimal(str(value))
                        except:
                            return Decimal('0.00')
                    
                    basic_pay = get_decimal_value(row[col_map['basic_pay']])
                    hra = get_decimal_value(row[col_map['hra']])
                    variable_pay = get_decimal_value(row[col_map['variable_pay']])
                    special_allowance = get_decimal_value(row[col_map.get('special_allowance', 0)])
                    other_allowances = get_decimal_value(row[col_map.get('other_allowances', 0)])
                    
                    # Create salary component
                    salary = SalaryComponent.objects.create(
                        employee=employee,
                        basic_pay=basic_pay,
                        hra=hra,
                        variable_pay=variable_pay,
                        special_allowance=special_allowance,
                        other_allowances=other_allowances
                    )
                    
                    # Calculate salary
                    salary.calculate_salary()
                    
                    employees_created += 1
                    
                except Exception as e:
                    self.errors.append(f"Row {row_idx}: Error processing employee - {str(e)}")
                    continue
            
            # Update upload instance
            self.upload_instance.total_employees = employees_created
            self.upload_instance.status = 'completed'
            self.upload_instance.processed_date = timezone.now()
            self.upload_instance.save()
            
            return True, employees_created
            
        except Exception as e:
            self.errors.append(f"Error parsing Excel file: {str(e)}")
            self.upload_instance.status = 'failed'
            self.upload_instance.error_message = str(e)
            self.upload_instance.save()
            return False, 0


class ReportGenerator:
    """Class to generate payroll reports"""
    
    def __init__(self, upload_instance):
        self.upload_instance = upload_instance
        self.employees = Employee.objects.filter(upload=upload_instance).select_related('salary')
    
    def generate_excel_report(self):
        """Generate Excel report"""
        try:
            # Create workbook
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.title = "Payroll Report"
            
            # Define styles
            header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            header_font = Font(bold=True, color="FFFFFF", size=11)
            border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            
            # Headers
            headers = [
                'Employee ID', 'Name', 'Email', 'Department', 'Designation',
                'Basic Pay', 'HRA', 'Variable Pay', 'Special Allowance', 'Other Allowances',
                'Gross Salary', 'PF', 'Professional Tax', 'Income Tax', 'Other Deductions',
                'Total Deductions', 'Net Salary', 'Take Home Pay'
            ]
            
            # Write headers
            for col_idx, header in enumerate(headers, start=1):
                cell = sheet.cell(row=1, column=col_idx)
                cell.value = header
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal='center', vertical='center')
                cell.border = border
            
            # Write data
            for row_idx, employee in enumerate(self.employees, start=2):
                salary = employee.salary
                
                data = [
                    employee.employee_id,
                    employee.name,
                    employee.email or '',
                    employee.department or '',
                    employee.designation or '',
                    float(salary.basic_pay),
                    float(salary.hra),
                    float(salary.variable_pay),
                    float(salary.special_allowance),
                    float(salary.other_allowances),
                    float(salary.gross_salary),
                    float(salary.provident_fund),
                    float(salary.professional_tax),
                    float(salary.income_tax),
                    float(salary.other_deductions),
                    float(salary.total_deductions),
                    float(salary.net_salary),
                    float(salary.take_home_pay)
                ]
                
                for col_idx, value in enumerate(data, start=1):
                    cell = sheet.cell(row=row_idx, column=col_idx)
                    cell.value = value
                    cell.border = border
                    
                    # Format currency columns
                    if col_idx >= 6:
                        cell.number_format = '₹#,##0.00'
                        cell.alignment = Alignment(horizontal='right')
                    else:
                        cell.alignment = Alignment(horizontal='left')
            
            # Auto-adjust column widths
            for column in sheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                sheet.column_dimensions[column_letter].width = adjusted_width
            
            # Add summary section
            summary_row = len(self.employees) + 3
            sheet.cell(row=summary_row, column=1).value = "SUMMARY"
            sheet.cell(row=summary_row, column=1).font = Font(bold=True, size=12)
            
            # Calculate totals
            total_gross = sum(e.salary.gross_salary for e in self.employees)
            total_deductions = sum(e.salary.total_deductions for e in self.employees)
            total_net = sum(e.salary.net_salary for e in self.employees)
            
            summary_data = [
                ("Total Employees", len(self.employees)),
                ("Total Gross Salary", float(total_gross)),
                ("Total Deductions", float(total_deductions)),
                ("Total Net Salary", float(total_net))
            ]
            
            for idx, (label, value) in enumerate(summary_data, start=1):
                sheet.cell(row=summary_row + idx, column=1).value = label
                sheet.cell(row=summary_row + idx, column=1).font = Font(bold=True)
                cell = sheet.cell(row=summary_row + idx, column=2)
                cell.value = value
                if isinstance(value, (int, float)) and label != "Total Employees":
                    cell.number_format = '₹#,##0.00'
            
            # Save to BytesIO
            excel_file = BytesIO()
            workbook.save(excel_file)
            excel_file.seek(0)
            
            # Create PayrollReport record
            filename = f"payroll_report_{self.upload_instance.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            report = PayrollReport.objects.create(
                upload=self.upload_instance,
                report_type='excel',
                file_size=excel_file.getbuffer().nbytes
            )
            
            report.file.save(filename, ContentFile(excel_file.read()), save=True)
            
            return report
            
        except Exception as e:
            raise Exception(f"Error generating Excel report: {str(e)}")
    
    def generate_pdf_report(self):
        """Generate PDF report"""
        try:
            # Create PDF buffer
            pdf_buffer = BytesIO()
            
            # Create document
            doc = SimpleDocTemplate(
                pdf_buffer,
                pagesize=A4,
                rightMargin=30,
                leftMargin=30,
                topMargin=30,
                bottomMargin=30
            )
            
            # Container for elements
            elements = []
            
            # Styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#4472C4'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#4472C4'),
                spaceAfter=12,
                spaceBefore=12
            )
            
            # Title
            title = Paragraph("Payroll Report", title_style)
            elements.append(title)
            
            # Report info
            info_data = [
                ['Report Date:', timezone.now().strftime('%B %d, %Y')],
                ['Upload ID:', str(self.upload_instance.id)],
                ['Total Employees:', str(len(self.employees))],
                ['Processed By:', self.upload_instance.user.get_full_name() or self.upload_instance.user.username]
            ]
            
            info_table = Table(info_data, colWidths=[2*inch, 4*inch])
            info_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#4472C4')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            
            elements.append(info_table)
            elements.append(Spacer(1, 20))
            
            # Employee details
            for employee in self.employees:
                salary = employee.salary
                
                # Employee header
                emp_heading = Paragraph(f"{employee.name} ({employee.employee_id})", heading_style)
                elements.append(emp_heading)
                
                # Employee info
                emp_info = []
                if employee.email:
                    emp_info.append(['Email:', employee.email])
                if employee.department:
                    emp_info.append(['Department:', employee.department])
                if employee.designation:
                    emp_info.append(['Designation:', employee.designation])
                
                if emp_info:
                    emp_info_table = Table(emp_info, colWidths=[1.5*inch, 4*inch])
                    emp_info_table.setStyle(TableStyle([
                        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                        ('TEXTCOLOR', (0, 0), (0, -1), colors.grey),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ]))
                    elements.append(emp_info_table)
                    elements.append(Spacer(1, 10))
                
                # Salary breakdown
                salary_data = [
                    ['Component', 'Amount (₹)'],
                    ['Basic Pay', f'{salary.basic_pay:,.2f}'],
                    ['HRA', f'{salary.hra:,.2f}'],
                    ['Variable Pay', f'{salary.variable_pay:,.2f}'],
                    ['Special Allowance', f'{salary.special_allowance:,.2f}'],
                    ['Other Allowances', f'{salary.other_allowances:,.2f}'],
                    ['Gross Salary', f'{salary.gross_salary:,.2f}'],
                    ['', ''],
                    ['Provident Fund', f'{salary.provident_fund:,.2f}'],
                    ['Professional Tax', f'{salary.professional_tax:,.2f}'],
                    ['Income Tax', f'{salary.income_tax:,.2f}'],
                    ['Other Deductions', f'{salary.other_deductions:,.2f}'],
                    ['Total Deductions', f'{salary.total_deductions:,.2f}'],
                    ['', ''],
                    ['Net Salary', f'{salary.net_salary:,.2f}'],
                    ['Take Home Pay', f'{salary.take_home_pay:,.2f}'],
                ]
                
                salary_table = Table(salary_data, colWidths=[3*inch, 2*inch])
                salary_table.setStyle(TableStyle([
                    # Header
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    
                    # Body
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
                    
                    # Gross salary row
                    ('BACKGROUND', (0, 6), (-1, 6), colors.HexColor('#E7E6E6')),
                    ('FONTNAME', (0, 6), (-1, 6), 'Helvetica-Bold'),
                    
                    # Total deductions row
                    ('BACKGROUND', (0, 12), (-1, 12), colors.HexColor('#E7E6E6')),
                    ('FONTNAME', (0, 12), (-1, 12), 'Helvetica-Bold'),
                    
                    # Final rows
                    ('BACKGROUND', (0, 14), (-1, -1), colors.HexColor('#4472C4')),
                    ('TEXTCOLOR', (0, 14), (-1, -1), colors.whitesmoke),
                    ('FONTNAME', (0, 14), (-1, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 14), (-1, -1), 10),
                    
                    # Grid
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 8),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                
                elements.append(salary_table)
                elements.append(PageBreak())
            
            # Summary page
            summary_heading = Paragraph("Summary", title_style)
            elements.append(summary_heading)
            
            total_gross = sum(e.salary.gross_salary for e in self.employees)
            total_deductions = sum(e.salary.total_deductions for e in self.employees)
            total_net = sum(e.salary.net_salary for e in self.employees)
            
            summary_data = [
                ['Metric', 'Value'],
                ['Total Employees', str(len(self.employees))],
                ['Total Gross Salary', f'₹{total_gross:,.2f}'],
                ['Total Deductions', f'₹{total_deductions:,.2f}'],
                ['Total Net Salary', f'₹{total_net:,.2f}'],
                ['Average Gross Salary', f'₹{total_gross/len(self.employees):,.2f}'],
                ['Average Net Salary', f'₹{total_net/len(self.employees):,.2f}'],
            ]
            
            summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 11),
                ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ]))
            
            elements.append(summary_table)
            
            # Build PDF
            doc.build(elements)
            
            # Get PDF content
            pdf_buffer.seek(0)
            pdf_content = pdf_buffer.read()
            
            # Create PayrollReport record
            filename = f"payroll_report_{self.upload_instance.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            report = PayrollReport.objects.create(
                upload=self.upload_instance,
                report_type='pdf',
                file_size=len(pdf_content)
            )
            
            report.file.save(filename, ContentFile(pdf_content), save=True)
            
            return report
            
        except Exception as e:
            raise Exception(f"Error generating PDF report: {str(e)}")