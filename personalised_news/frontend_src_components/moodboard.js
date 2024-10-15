import React, { useState, useEffect } from 'react';

const MoodBoard = () => {
    const [articles, setArticles] = useState([]);
    const [selectedMood, setSelectedMood] = useState('happy');

    useEffect(() => {
        fetch(`http://your-backend-url/api/news/${selectedMood}`)
            .then(response => response.json())
            .then(data => setArticles(data));
    }, [selectedMood]);

    return (
        <div>
            <div className="mood-selector">
                <button onClick={() => setSelectedMood('happy')}>😊 Happy</button>
                <button onClick={() => setSelectedMood('sad')}>😢 Sad</button>
                <button onClick={() => setSelectedMood('angry')}>😡 Angry</button>
                <button onClick={() => setSelectedMood('surprised')}>😮 Surprised</button>
            </div>
            <div className="news-articles">
                {articles.map(article => (
                    <div key={article.title}>
                        <h3>{article.title}</h3>
                        <p>{article.content}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default MoodBoard;
