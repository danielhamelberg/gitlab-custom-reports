import pandas as pd

# Read the report data
df = pd.read_csv("pipeline_report.csv")

# Generate the HTML page
html = """
<html>
  <head>
    <title>Pipeline Report</title>
  </head>
  <body>
    <h1>Pipeline Report</h1>
    <table>
      <thead>
        <tr>
          <th>STAGE</th>
          <th>ENVIRONMENT</th>
          <th>2022</th>
          <th>2021</th>
          <th>Percent Change</th>
        </tr>
      </thead>
      <tbody>
"""

for index, row in df.iterrows():
    html += """
        <tr>
          <td>{}</td>
          <td>{}</td>
          <td>{}</td>
          <td>{}</td>
          <td>{:.2f}%</td>
        </tr>
    """.format(row["STAGE"], row["ENVIRONMENT"], row["count_2022"], row["count_2021"], row["percent_change"])

html += """
      </tbody>
    </table>
  </body>
</html>
"""

# Write the HTML page to a file
with open("index.html", "w") as f:
    f.write(html)
