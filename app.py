from flask import Flask, redirect, url_for, render_template, session, send_file, Response, stream_with_context
from flask_wtf import FlaskForm
from wtforms.fields.html5 import DateField, TimeField
from wtforms import validators, SubmitField, StringField
import datetime

app = Flask(__name__)

app.config['SECRET_KEY'] = '&*(j*(JUGTY8*'


class InfoForm(FlaskForm):
    part_numbers = StringField('Part Numbers', description='Comma seperated list of part numbers')
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=(validators.DataRequired(),))
    start_time = TimeField('Time', format='%H:%M', validators=(validators.DataRequired(),))
    end_date = DateField('End Date', format='%Y-%m-%d', validators=(validators.DataRequired(),))
    end_time = TimeField('Time', format='%H:%M', validators=(validators.DataRequired(),))
    submit = SubmitField('Submit')


@app.route('/', methods=['GET', 'POST'])
def index():
    def generate(start, end, part_numbers):
        # create and return your data in small parts here
        import mysql.connector
        config = {
            'user': 'prodmon',
            'password': 'pm258',
            'host': '10.4.1.245',
            'port': 6601,
            'database': 'prod_mon',
            'raise_on_warnings': True
        }

        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        query = ("SELECT * FROM 1730_Vantage "
                 "WHERE part_number IN (%s) "
                 "AND created_at BETWEEN %s AND %s")

        #part_numbers = '50-8670'

        # start_dt = datetime.datetime(2021, 7, 20, 6, 0, 0)
        # end_dt = datetime.datetime(2021, 7, 20, 14, 0, 0)
        print('Partnumbers', part_numbers)
        cursor.execute(query, (part_numbers, start, end))

        comma_header = ('ID,created at,part number,laser data,'
                        'Date,Time,Part Number,Date stamp,Media presence- Braze pellet holes,'
                        'Lube holes,Media presence- Pellet holes,Spot face check,Pinion crosshole presence,'
                        'Induction hardening presence,Balance hole position,Media presence bal hole,'
                        'Witness mark,Media presence pinion holes,Media presence web slot,'
                        'Media presence windows,Media presence Machined Recess plate side,'
                        'Media presence blind ped. Holes,Media presence slot at pinion hole,'
                        'Media presence blind pellet holes,Window height A,status,Window height B,status,'
                        'Window height C,status,Window height D,status,Window height E,status,'
                        'Window height Max,Window height Min,Pedestal side Pinion Holes OK,'
                        'Staking pocket presence,Media presence Machined recess pedestal side,'
                        'Pedestal side Machined pocket holes,Eddy Current Result,Resonance Result,'
                        'Plate pinion hole a dia.,status,Plate pinion hole b dia.,status,'
                        'Plate pinion hole c dia.,status,Plate pinion hole d dia.,status,'
                        'Plate pinion hole e dia.,status,Pedestal pinion hole a dia.,status,'
                        'Pedestal pinion hole b dia.,status,Pedestal pinion c dia.,status,'
                        'Pedestal pinion hole d dia.,status,Pedestal pinion hole e dia.,status,Bushing ID,'
                        'status,Upper ID,status,Lower ID,statusLaser Result,statusLaser Grade,'
                        'statusBarcode Mark,status\n')

        yield comma_header

        for (id, created_at, part_number, laser_data, inspection_data) in cursor:
            row = str(id) + ','
            row += created_at.isoformat() + ','
            row += part_number + ','
            row += laser_data + ','
            inspection_data = inspection_data.replace('\t', ',')
            row += inspection_data + ','
            row += '\n'
            yield row

        cursor.close()
        cnx.close()
        # for i in range(10000):
        #      yield str(i) + ', '
        #
        # yield 'done'
        #
        # cnx.close()

    form = InfoForm()
    if form.is_submitted():
        print("submitted")
    if form.validate():
        print("valid")
    print(form.errors)
    if form.validate_on_submit():
        start = datetime.datetime.combine(form.start_date.data, form.start_time.data)
        end = datetime.datetime.combine(form.end_date.data, form.end_time.data)
        part_numbers = form.part_numbers.data

        # start = datetime.datetime(2021, 7, 20, 6, 0, 0)
        # end = datetime.datetime(2021, 7, 20, 14, 0, 0)

        response = Response(generate(start, end, part_numbers), mimetype='text/csv')
        response.headers['Content-Disposition'] = 'attachment; filename=result.csv'
        return response
    return render_template('index.html', form=form)


if __name__ == '__main__':
    # run app in debug mode on port 5000
    app.run(debug=True)
