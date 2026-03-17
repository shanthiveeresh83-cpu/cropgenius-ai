import { Bar } from "react-chartjs-2";
import { useEffect, useState } from "react";
function Dashboard() {
  const [chartData, setChartData] = useState({});
  useEffect(() => {
    fetch("http://localhost:5000
      .then(res => res.json())
      .then(data => {
        setChartData({
          labels: Object.keys(data),
          datasets: [
            {
              label: "Crop Recommendations",
              data: Object.values(data),
              backgroundColor: "green"
            }
          ]
        });
      });
  }, []);
  return (
    <div>
      <h2>📊 Recommendation Dashboard</h2>
      <Bar data={chartData} />
    </div>
  );
}
export default Dashboard;