import {useEffect,useState} from "react";
import {getSignals} from "../services/api";

export default function Dashboard(){

const [signals,setSignals]=useState([]);

useEffect(()=>{
 loadSignals();
},[]);

async function loadSignals(){
 const data=await getSignals();
 setSignals(data);
}

return(
<div>

<h2>Signals</h2>

{
signals.map((s)=>(
<div key={s.signal_id}>

<p>{s.signal_id}</p>

<p>{s.risk_level}</p>

<p>{s.anomaly_type}</p>

</div>
))
}

</div>
)

}