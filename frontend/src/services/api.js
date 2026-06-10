const API =
import.meta.env.VITE_SAMACHAR_API;


export async function getSignals(){

const response=
await fetch(`${API}/signals`);

return response.json();

}


export async function getPatterns(){

const response=
await fetch(`${API}/patterns`);

return response.json();

}


export async function triggerAction(data){

const response=
await fetch(
`${API}/action`,
{
method:"POST",

headers:{
"Content-Type":
"application/json"
},

body:
JSON.stringify(data)

}
);

return response.json();

}