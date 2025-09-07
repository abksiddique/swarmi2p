#!/usr/bin/env bash
# i2pmetadata-4-17-25-final.sh
#
# Live‑capture IP packets on enp0s3 and write:
# Time(YYYY‑MM‑DD HH:MM:SS),Src IP,Src Port,Dst IP,Dst Port,Proto,TTL,PacketSize(Bytes)
# into i2pmetadata-4-17-25-final.csv in the same folder.

set -euo pipefail

# derive base name and output file
SCRIPT_BASE="$(basename "$0" .sh)"
OUTFILE="${SCRIPT_BASE}.csv"

# write header
echo "Time,Src IP,Src Port,Dst IP,Dst Port,Proto,TTL,PacketSize(Bytes)" > "$OUTFILE"

echo "Starting live capture on enp0s3… output → $OUTFILE"
sudo tshark -i enp0s3 -n -l \
  -T fields -E separator=, \
  -e frame.time_epoch \
  -e ip.src \
  -e tcp.srcport \
  -e udp.srcport \
  -e ip.dst \
  -e tcp.dstport \
  -e udp.dstport \
  -e _ws.col.Protocol \
  -e ip.ttl \
  -e frame.len \
  -Y "ip" \
| awk -F, 'BEGIN{OFS=","}
{
  # split off seconds portion
  split($1,a,"."); 
  # convert to human date
  cmd = "date -d @" a[1] " +\"%Y-%m-%d %H:%M:%S\"";
  cmd | getline dt; 
  close(cmd);
  # replace epoch with human timestamp
  $1 = dt;
  print;
}' \
| tee -a "$OUTFILE"

