import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import './SalesDashboard.css';

const days = [
  'Monday',
  'Tuesday',
  'Wednesday',
  'Thursday',
  'Friday',
  'Saturday',
  'Sunday',
];
const colors = [
  '#FF6B6B',
  '#4ECDC4',
  '#45B7D1',
  '#FFA07A',
  '#98D8C8',
  '#F06292',
  '#AED581',
];

const SalesDashboard = () => {
  const [data, setData] = useState([]);
  const [visibleDays, setVisibleDays] = useState(
    days.reduce((acc, day) => ({ ...acc, [day]: true }), {})
  );
  const [isHourlyView, setIsHourlyView] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setIsLoading(true);
    fetch('/processed_sales_data.json')
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then((jsonData) => {
        setData(jsonData);
        setIsLoading(false);
      })
      .catch((e) => {
        console.error('Fetching error:', e);
        setError(e.message);
        setIsLoading(false);
      });
  }, []);

  const toggleDay = (day) => {
    setVisibleDays((prev) => {
      const newState = { ...prev, [day]: !prev[day] };
      // Ensure at least one day is always visible
      if (Object.values(newState).every((v) => !v)) {
        return { ...prev };
      }
      return newState;
    });
  };

  const toggleHourlyView = () => {
    setIsHourlyView(!isHourlyView);
  };

  const processData = (rawData) => {
    if (!isHourlyView) return rawData;

    const hourlyData = [];
    for (let i = 0; i < rawData.length; i += 2) {
      const hourData = { time: rawData[i].time.slice(0, -3) };
      days.forEach((day) => {
        hourData[day] = (rawData[i][day] || 0) + (rawData[i + 1]?.[day] || 0);
      });
      hourlyData.push(hourData);
    }
    return hourlyData;
  };

  const processedData = processData(data);

  if (isLoading) return <div className='loading'>กำลังโหลด...</div>;
  if (error) return <div className='error'>เกิดข้อผิดพลาด: {error}</div>;

  const visibleData = processedData.map((item) => {
    const newItem = { time: item.time };
    days.forEach((day) => {
      if (visibleDays[day]) {
        newItem[day] = item[day];
      }
    });
    return newItem;
  });

  return (
    <div className='sales-dashboard'>
      <div className='dashboard-header'>
        <h2 className='dashboard-title'>แดชบอร์ดยอดขาย</h2>
        <div className='dashboard-controls'>
          <button onClick={toggleHourlyView}>
            {isHourlyView ? 'ดูแบบครึ่งชั่วโมง' : 'ดูแบบชั่วโมง'}
          </button>
        </div>
      </div>
      <div className='day-toggles'>
        {days.map((day, index) => (
          <label key={day} style={{ color: colors[index] }}>
            <input
              type='checkbox'
              checked={visibleDays[day]}
              onChange={() => toggleDay(day)}
            />
            {day}
          </label>
        ))}
      </div>
      <div className='chart-container'>
        {Object.values(visibleDays).some((v) => v) ? (
          <ResponsiveContainer width='100%' height='100%'>
            <LineChart data={visibleData}>
              <CartesianGrid strokeDasharray='3 3' />
              <XAxis dataKey='time' />
              <YAxis />
              <Tooltip />
              <Legend />
              {days.map(
                (day, index) =>
                  visibleDays[day] && (
                    <Line
                      key={day}
                      type='monotone'
                      dataKey={day}
                      stroke={colors[index]}
                      strokeWidth={2}
                      dot={true}
                      activeDot={true}
                    />
                  )
              )}
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className='no-data'>
            ไม่มีข้อมูลที่จะแสดง กรุณาเลือกวันอย่างน้อยหนึ่งวัน
          </div>
        )}
      </div>
    </div>
  );
};

export default SalesDashboard;
