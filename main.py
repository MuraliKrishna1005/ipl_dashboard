from flask import Flask, render_template_string, request, render_template
from io import BytesIO
import base64
import sqlite3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

app = Flask(__name__)

# Connect to SQLite database
conn = sqlite3.connect('cricket_data.db')
cur = conn.cursor()

def get_all_stats():
    # Execute a SELECT query to retrieve all data
    cur.execute('''SELECT * FROM bowl2bowl_stats''')
    # Fetch all rows from the result
    rows = cur.fetchall()
    return rows

batsmen_over_data = {}
def update_batsmen(over_no,batter,run,wicket):
    if batter not in batsmen_over_data:
        batsmen_over_data[batter] = {i: {'runs': 0, 'balls': 0, 'wicket':0} for i in range(20)}
    batsmen_over_data[batter][over_no]['runs'] += run
    batsmen_over_data[batter][over_no]['balls'] += 1
    batsmen_over_data[batter][over_no]['wicket'] += wicket

bowler_over_data = {}
def update_bowler(over_no,bowler,run,wicket):
    if bowler not in bowler_over_data:
        bowler_over_data[bowler] = {i: {'runs': 0, 'balls': 0, 'wicket':0} for i in range(20)}
    bowler_over_data[bowler][over_no]['runs'] += run
    bowler_over_data[bowler][over_no]['balls'] += 1
    bowler_over_data[bowler][over_no]['wicket'] += wicket

# Example usage
all_stats = get_all_stats()
for row in all_stats:
    over_no = row[2]
    batter = row[4]
    bowler = row[5]
    run = row[6]
    wicket = row[8]
    update_batsmen(over_no,batter,run,wicket)
    update_bowler(over_no,bowler,run,wicket)

# Close connection
conn.close()

#home
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/batsman_dashboard', methods=['GET', 'POST'])
def batsman_dashboard():
    if request.method == 'POST':
        selected_batsman = request.form['batsman']
        runs_scored = [batsmen_over_data[selected_batsman][i]['runs'] for i in range(20)]
        return render_template_string(
            '''
            <h1>Batsman Runs Dashboard</h1>
            <form method="post">
                <label for="batsman">Select a batsman:</label>
                <select name="batsman" id="batsman">
                    {% for batsman in batsmen %}
                    <option value="{{ batsman }}" {% if selected_batsman == batsman %}selected{% endif %}>{{ batsman }}</option>
                    {% endfor %}
                </select>
                <input type="submit" value="Plot">
            </form>
            <div>
                <h2>Runs scored by {{ selected_batsman }} at each over</h2>
                <img src="data:image/png;base64,{{ plot_data }}" alt="Plot">
            </div>
            ''',
            batsmen=list(batsmen_over_data.keys()),
            selected_batsman=selected_batsman,
            plot_data=plot_batsman_runs(selected_batsman)
        )
    else:
        return render_template_string(
            '''
            <h1>Batsman Runs Dashboard</h1>
            <form method="post">
                <label for="batsman">Select a batsman:</label>
                <select name="batsman" id="batsman">
                    {% for batsman in batsmen %}
                    <option value="{{ batsman }}">{{ batsman }}</option>
                    {% endfor %}
                </select>
                <input type="submit" value="Plot">
            </form>
            '''
            ,batsmen=list(batsmen_over_data.keys())
        )

def plot_batsman_runs(batsman):
    runs_scored = [batsmen_over_data[batsman][i]['runs'] for i in range(20)]
    plt.plot(range(20), runs_scored, marker='o')
    for i, txt in enumerate(runs_scored):
        plt.text(i, txt, str(txt), ha='center', va='bottom')
    plt.title(f"Total Runs scored by {batsman} is {sum(runs_scored)}")
    plt.xlabel('Overs')
    plt.ylabel('Runs')
    plt.xticks(range(20))  # Set x-axis ticks to whole numbers
    plt.grid(True)

    # Convert plot to base64 encoded string
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plot_data = base64.b64encode(buffer.getvalue()).decode()
    plt.close()

    return plot_data

@app.route('/bowler_dashboard', methods=['GET', 'POST'])
def bowler_dashboard():
    if request.method == 'POST':
        selected_bowler = request.form['bowler']
        runs_scored = [bowler_over_data[selected_bowler][i]['wicket'] for i in range(20)]
        return render_template_string(
            '''
            <h1>Bowler Dismissal Dashboard</h1>
            <form method="post">
                <label for="bowler">Select a bowler:</label>
                <select name="bowler" id="bowler">
                    {% for bowler in bowlers %}
                    <option value="{{ bowler }}" {% if selected_bowler == bowler %}selected{% endif %}>{{ bowler }}</option>
                    {% endfor %}
                </select>
                <input type="submit" value="Plot">
            </form>
            <div>
                <h2>Dismissals by {{ selected_bowler }} at each over</h2>
                <img src="data:image/png;base64,{{ plot_data }}" alt="Plot">
            </div>
            ''',
            bowlers=list(bowler_over_data.keys()),
            selected_bowler=selected_bowler,
            plot_data=plot_bowler_dismissals(selected_bowler)
        )
    else:
        return render_template_string(
            '''
            <h1>Bowler Dismissal Dashboard</h1>
            <form method="post">
                <label for="bowler">Select a bowler:</label>
                <select name="bowler" id="bowler">
                    {% for bowler in bowlers %}
                    <option value="{{ bowler }}">{{ bowler }}</option>
                    {% endfor %}
                </select>
                <input type="submit" value="Plot">
            </form>
            '''
            ,bowlers=list(bowler_over_data.keys())
        )

def plot_bowler_dismissals(bowler):
    wickets_taken = [bowler_over_data[bowler][i]['wicket'] for i in range(20)]
    plt.plot(range(20), wickets_taken, marker='o')
    plt.title(f"Total Dismissals of {bowler} is {sum(wickets_taken)}")
    plt.xlabel('Overs')
    plt.ylabel('Wickets')
    plt.xticks(range(20))
    plt.grid(True)

    # Convert plot to base64 encoded string
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plot_data = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    return plot_data

if __name__ == '__main__':
    app.run(debug=True)
