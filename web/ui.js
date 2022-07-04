ga = [];
gap = [];
function getApi(id,action,values) { 
	if(!values) values="?tm="+Math.random();
	else values=values+"&tm="+Math.random();
	pass = document.getElementById("password").value;
	if(pass != ""){
		document.getElementById(id).innerHTML="";
		values = values + "&pass=" + pass;
		if (window.XMLHttpRequest) { ga[id]=new XMLHttpRequest(); }
		else { ga[id]=new ActiveXObject("Microsoft.XMLHTTP"); }
		ga[id].onreadystatechange=function() {
			if (ga[id].readyState==4 && ga[id].status==200) {
				var result=ga[id].responseText;		
				var values=JSON.parse(result);	
				if(!values.error){
					if(values.html) {
						document.getElementById(id).innerHTML=values.html;
					}
					if(values.cmd){
						for(var c=0;c<values.cmd.length;c++){
							console.log("Eval: "+values.cmd[c]);
							eval(values.cmd[c]);
						}
					}
					
				}
				else{
					document.getElementById(id).innerHTML=values.error;
				}	
			}
		}
		ga[id].open("GET",action+values,true);
		ga[id].send();	
	
	}
	else {
		alert("Security password must be entered.")
	}		
}
function getApiPlayer(id,action,values) { 
	if(!values) values="?tm="+Math.random();
	else values=values+"&tm="+Math.random();
	document.getElementById(id).innerHTML="";
	if (window.XMLHttpRequest) { gap[id]=new XMLHttpRequest(); }
	else { gap[id]=new ActiveXObject("Microsoft.XMLHTTP"); }
	gap[id].onreadystatechange=function() {
		if (gap[id].readyState==4 && gap[id].status==200) {
			var result=gap[id].responseText;		
			var values=JSON.parse(result);	
			if(!values.error){
				document.getElementById(id).innerHTML=values.result;
				if(values.cmd){
					for(var c=0;c<values.cmd.length;c++){
						console.log("Eval: "+values.cmd[c]);
						eval(values.cmd[c]);
					}
				}
				
			}
			else{
				document.getElementById(id).innerHTML=values.error;
			}	
		}
	}
	gap[id].open("GET",action+values,true);
	gap[id].send();	
}
function getApiList(id,path) { 
	if(!path) values="?tm="+Math.random();
	else values="?path="+path+"&tm="+Math.random();
	document.getElementById(id).innerHTML="Loading...";
	if (window.XMLHttpRequest) { gap[id]=new XMLHttpRequest(); }
	else { gap[id]=new ActiveXObject("Microsoft.XMLHTTP"); }
	gap[id].onreadystatechange=function() {
		if (gap[id].readyState==4 && gap[id].status==200) {
			var result=gap[id].responseText;		
			var values=JSON.parse(result);	
			if(!values.error){
				document.getElementById("listPath").value=values.path;
				document.getElementById("listFiles").innerHTML="";
				for (x = 0; x < values.files.length; x++){
					item = values.files[x]
					document.getElementById("listFiles").innerHTML+='<li><a href="#" onclick="getApiPlayer(\'output\',\'/api/play\',\'?file='+values.path+'/'+item+'\')">'+item.replaceAll("_"," ")+'</a></li>';
				}				
				document.getElementById("listDirs").innerHTML="";
				if(values.path != ""){
					d=values.path+"DELETEME"
					s=d.split("/");
					p=d.replace("/"+s[s.length-1],"")
					document.getElementById("listDirs").innerHTML+='<li class="back"><a href="#" onclick="getApiList(\'output\',\''+p+'\')">Back ..</a></li>';
				}
				for (x = 0; x < values.directories.length; x++){
					item = values.directories[x]
					document.getElementById("listDirs").innerHTML+='<li><a href="#" onclick="getApiList(\'output\',\''+values.path+'/'+item+'\')">'+item.replaceAll("_"," ")+'</a></li>';
				}
				document.getElementById(id).innerHTML="Directory listing done.";
			}
			else{
				document.getElementById(id).innerHTML=values.error;
			}	
		}
	}
	gap[id].open("GET","/api/files"+values,true);
	gap[id].send();	

}
function getPlaylistMode(){
	if(document.getElementById("playlistmode").value=="0"){
		getApiPlayer('output','/api/playall','?path='+document.getElementById('listPath').value);
	}
	else{
		getApiPlayer('output','/api/playall','?path=stop')
	}
}
function getPlayer(id) { 
	if (window.XMLHttpRequest) { gPlayer=new XMLHttpRequest(); }
	else { gPlayer=new ActiveXObject("Microsoft.XMLHTTP"); }
	gPlayer.onreadystatechange=function() {
		if (gPlayer.readyState==4 && gPlayer.status==200) {
			var result=gPlayer.responseText;		
			var values=JSON.parse(result);	
			if(!values.error){
				document.getElementById("playlistmode").value=values.playlist;
				if(values.playing==1){
					document.getElementById("playerPlaying").src="imgs/pause.png";
					document.getElementById("playerPosition").style.backgroundSize=values.position+"% 100%";
					document.getElementById("playerPosition").innerHTML=values.position+"%";
				}
				else{
					document.getElementById("playerPlaying").src="imgs/play.png";
					document.getElementById("playerPosition").style.backgroundSize="0% 100%";
					document.getElementById("playerPosition").innerHTML="Not playing";
				}
				
				if(values.mute==1){
					document.getElementById("playerMute").src="imgs/mute_big.png";
				}
				else{
					document.getElementById("playerMute").src="imgs/sound.png";
				}
				if(values.playlist==1){
					document.getElementById("playerPlaylist").style.background="#000";
				}
				else{
					document.getElementById("playerPlaylist").style.background="none";
				}
				document.getElementById("playerTime").innerHTML=values.time;
				document.getElementById("playerTimeTotal").innerHTML=values.totaltime;
				document.getElementById("playerTitle").innerHTML=values.title.replaceAll("_"," ");
				document.getElementById("playerVolume").innerHTML=values.volume+"%";
				
				if(values.cmd){
					for(var c=0;c<values.cmd.length;c++){
						console.log("Eval: "+values.cmd[c]);
						eval(values.cmd[c]);
					}
				}
			}
			else{
				document.getElementById(id).innerHTML=values.error;
			}	
			setTimeout("getPlayer('output')",1000);
		}
	}
	gPlayer.open("GET","api/info?"+Math.random(),true);
	gPlayer.send();	
}

function showStats(){
	if(document.getElementById("stats").style.display=="none"){
		document.getElementById("stats").style.display="inline-block";
	}
	else{
		document.getElementById("stats").style.display="none";
	}		
}

function geStats(id) { 
	if (window.XMLHttpRequest) { gStats=new XMLHttpRequest(); }
	else { gStats=new ActiveXObject("Microsoft.XMLHTTP"); }
	gStats.onreadystatechange=function() {
		if (gStats.readyState==4 && gStats.status==200) {
			var result=gStats.responseText;		
			var values=JSON.parse(result);	
			if(!values.error){
				document.getElementById("statsCPUSpeed").innerHTML=values.cpuspeed;
				document.getElementById("statsCPUTemp").innerHTML=values.cputemp;
				document.getElementById("statsRAMFree").innerHTML=values.ramfree;
				document.getElementById("statsRAMTotal").innerHTML=values.ramtotal;
				document.getElementById("statsSYSLoad").innerHTML=values.load;
				document.getElementById("statsSYSUptime").innerHTML=values.uptime;
				document.getElementById("statsSYSIP").innerHTML=values.ip;
			}
			else{
				document.getElementById(id).innerHTML=values.error;
			}	
			setTimeout("geStats('output')",10000);
		}
	}
	gStats.open("GET","stats.json?"+Math.random(),true);
	gStats.send();	
}


setTimeout("geStats('output')",2000);
setTimeout("getPlayer('output')",1000);
setTimeout("getApiList('output','');",1000);