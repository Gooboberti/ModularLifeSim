// MiniSimmy3 - Utility Functions

function generateSciFiName() {
  const prefixes = ['Kael','Vex','Thorne','Zyl','Ryn','Syl','Drak','Nyx','Korr','Vael','Sylas','Myr'];
  const suffixes = ['-9','-12','ara','ith','on','yx','ar','en','os','ix','ael','or'];
  return prefixes[floor(random(prefixes.length))] + suffixes[floor(random(suffixes.length))];
}

function formatDust(mg) {
  if (mg >= 1000000) return (mg / 1000000).toFixed(2) + " kg";
  if (mg >= 1000) return (mg / 1000).toFixed(2) + " g";
  return mg.toFixed(2) + " mg";
}