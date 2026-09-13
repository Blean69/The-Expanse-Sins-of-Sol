"""Prove source deployment axes differ from the new aiming joints."""
from geometry04_diagnose import *
m=read(ROOT/'audit/geometry03-b/hero-mount-metadata.json');C=np.array(m['normalization']['source_to_game_rotation']);rm=a.world[1];G=rm@local(2,0)@np.linalg.inv(rm@local(2,16.625));eq=read(ROOT/'audit/geometry03-b/hero-equipment-mounts.json');records=[]
for i,ni in enumerate([117,180,218,256,294,332]):
 D=G@rm@local(ni,16.625)@np.linalg.inv(rm@local(ni,0));rv=Rotation.from_matrix(D[:3,:3]).as_rotvec();axis=C@(rv/np.linalg.norm(rv));fw=np.array(eq['pdc_mounts'][i]['forward']);cos=abs(float(np.dot(axis,fw)));assert cos>.999999;records.append({'index':i,'source_node':ni,'degrees':float(np.degrees(np.linalg.norm(rv))),'axis_old_game_coordinates':axis.tolist(),'absolute_dot_with_actual_barrel_forward':cos,'interpretation':'Deployment rotation about barrel axis, not a game aiming yaw/pitch pivot'})
write(ROOT/'audit/geometry04-b/deployment-axis-evidence.json',records);print('All6 source deployment axes parallel actual barrel directions')
