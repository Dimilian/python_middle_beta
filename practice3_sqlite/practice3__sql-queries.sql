-- query1
SELECT a.name FROM actors as a
  JOIN movie_actors as ma
    ON ma.actor_id = a.id
  JOIN movies as m
    ON m.id = ma.movie_id
    WHERE m.director LIKE '%Lerdam%'

-- query2
SELECT w.name FROM movies as m
  INNER JOIN writers as w
    ON w.id = m.writer
    WHERE w.name != 'N/A'
GROUP BY m.writer
ORDER BY COUNT(m.writer) DESC


-- query3
SELECT COUNT(ma.actor_id), a.name FROM movie_actors as ma
  JOIN actors as a
    ON a.id = ma.actor_id
    WHERE a.name != 'N/A'
GROUP BY ma.actor_id
ORDER BY COUNT(ma.actor_id) DESC