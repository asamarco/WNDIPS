from flask import Flask, render_template_string
from apscheduler.schedulers.background import BackgroundScheduler
import subprocess
import threading
import sys
import atexit
import time

app = Flask(__name__)
scan_results = []
ip_range = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.0/24"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>WNDIPS</title>
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css">
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }
        h1 { color: #333; }
        h2 { color: #666; font-style: italic; }
        table { width: 100%; margin-top: 20px; }
    </style>
</head>
<body>
    <h1>WNDIPS</h1>
    <h2>Windows Network Discovery Is Plain S**t</h2>
    <table id="scanTable" class="display">
        <thead>
            <tr>
                <th>IP Address</th>
                <th>NetBIOS Name</th>
                <th>Server</th>
                <th>User</th>
                <th>MAC Address</th>
            </tr>
        </thead>
        <tbody>
            {% for row in results %}
            <tr>
                <td>{{ row[0] }}</td>
                <td>{{ row[1] }}</td>
                <td>{{ row[2] }}</td>
                <td>{{ row[3] }}</td>
                <td>{{ row[4] }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
    <script>
        $(document).ready(function() {
            $('#scanTable').DataTable({
                order: [[0, 'asc']]  // Sort by IP Address column
            });
        });
    </script>
</body>
<script>
  // Extend DataTables with IP address sorting
  jQuery.extend(jQuery.fn.dataTable.ext.type.order, {
    "ip-address-pre": function (ip) {
      if (!ip) return 0;
      const parts = ip.split('.');
      return parts.reduce((acc, part) => acc * 256 + parseInt(part, 10), 0);
    }
  });

  // Initialize DataTable safely
  function initScanTable() {
    const tableId = '#scanTable';

    // Destroy existing instance if needed
    if ($.fn.DataTable.isDataTable(tableId)) {
      $(tableId).DataTable().destroy();
    }

    // Reinitialize with IP sorting
    $(tableId).DataTable({
      columnDefs: [
        { type: 'ip-address', targets: 0 } // IP column
      ],
      order: [[0, 'asc']],
      pageLength: 25,
      responsive: true
    });
  }

  // Run on document ready
  $(document).ready(function () {
    initScanTable();
  });
</script>
</html>
"""


def run_nbtscan():
    global scan_results
    try:
        output = subprocess.check_output(['sudo', 'nbtscan', '-r', ip_range], text=True)
        lines = output.strip().split('\n')[3:]  # Skip header lines
        parsed = []
        for line in lines:
            parts = line.split()
            if len(parts) >= 2:
                ip = parts[0]
                name = parts[1]
                server = parts[2] if len(parts) > 2 else ''
                user = parts[3] if len(parts) > 3 else ''
                mac = parts[4] if len(parts) > 4 else ''
                parsed.append([ip, name, server, user, mac])
        scan_results = parsed
    except Exception as e:
        scan_results = [["Error", str(e), "", "", ""]]

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, results=scan_results)

if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_nbtscan, 'interval', minutes=5)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown(wait=False))  # Graceful shutdown

    run_nbtscan()  # Initial run

    # Run Flask in a thread
    flask_thread = threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 5000})
    flask_thread.start()

    # Keep main thread alive
    try:
        while flask_thread.is_alive():
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        print("Shutting down...")
