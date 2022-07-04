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

        # part_numbers = '50-8670'

        # start_dt = datetime.datetime(2021, 7, 20, 6, 0, 0)
        # end_dt = datetime.datetime(2021, 7, 20, 14, 0, 0)
        print('Partnumbers', part_numbers)
        cursor.execute(query, (part_numbers, start, end))

        comma_header = ('id, created_at, part_number, laser_data, part_fail, Date, Time, Part Number, '
                        'Date stamp, Overall Status, Media presence - Braze pellet holes, '
                        'Lube holes, Media presence - Pellet holes, Spot face check, '
                        'Pinion crosshole presence, Induction hardening presence, '
                        'Balance hole position, Media presence bal hole, Witness mark, '
                        'Media presence pinion holes, Media presence web slot, Media presence windows, '
                        'Media presence Machined Recess plate side, Media presence blind ped.Holes, '
                        'Media presence slot at pinion hole, Media presence blind pellet holes, '
                        'Window A Max, Window A Min, Window B Max, Window B Min, Window C Max, Window C Min, '
                        'Window D Max, Window D Min, Window E Max, Window E Min, W.Height status, Place holder, '
                        'Pedestal side Pinion Holes OK, Staking pocket presence, '
                        'Media presence Machined recess pedestal side, Pedestal side Machined pocket holes, '
                        'Eddy Current Result, Resonance Result, Plate pinion hole a dia., Pl.P A Status, '
                        'Plate pinion hole b dia., Pl.P B Status, Plate pinion hole c dia., Pl.P C Status, '
                        'Plate pinion hole d dia., Pl.P D Status, Plate pinion hole e dia., Pl.P E Status, '
                        'Pedestal pinion hole a dia., Pd. P A Status, Pedestal pinion hole b dia., Pd. P B Status, '
                        'Pedestal pinion hole c dia., Pd. P C Status, Pedestal pinion hole d dia., Pd. P D Status, '
                        'Pedestal pinion hole e dia., Pd. P E Status, Bushing ID, Bushing ID Status, '
                        'Upper ID, Upper ID Status, Lower ID, Lower ID Status, Laser Mark, Laser Grade, '
                        'Barcode Read, status15, status16\n')

        yield comma_header

        for (id, created_at, part_number, laser_data, part_fail, inspection_data) in cursor:
            row = str(id) + ','
            row += created_at.isoformat() + ','
            row += part_number + ','
            row += laser_data + ','
            row += part_fail + ','
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
