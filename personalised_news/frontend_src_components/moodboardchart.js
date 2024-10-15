import React from 'react';
import { Doughnut } from 'react-chartjs-2';

const MoodBoardChart = ({ data }) => {
    const chartData = {
        labels: ['Happy', 'Sad', 'Angry', 'Surprised'],
        datasets: [{
            data: data,  // Pass in emotional distribution data here
            backgroundColor: ['#FFD700', '#87CEFA', '#FF6347', '#DA70D6']
        }]
    };

    return <Doughnut data={chartData} />;
}

export default MoodBoardChart;
