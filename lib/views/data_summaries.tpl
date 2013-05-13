<div>
	return to <a href='/exerdata/home'>home</a> page
	</br></br>

	available data:
	
%if activities:
%	for activity in activities:
	<b>{{activity.id}}</b>
	
	<table border="1">
	<tr>
	<td>id</td>
	<td>{{activity.id}}</td>
	</tr>
	<tr>
	<td>type</td>
	<td>{{activity.type}}</td>
	</tr>
	<tr>
	<td>total distance</td>
	<td>{{activity.getDistAggregate()}}</td>
	</tr>
	<tr>
	<td>total time</td>
	<td>{{activity.getFormattedTime()}}</td>
	</tr>
	<tr>
	<td>average heart rate</td>
	<td>{{activity.getAverageHr()}}</td>
	</tr>
	<tr>
	<td>average pace</td>
	<td>{{activity.getAvgPace().toString()}}</td>
	</tr>
	</table>

</div>