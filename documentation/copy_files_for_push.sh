set -x

ENAME=MC_25km_jra_iaf-1.0-beta-5165c0f8
OFOL=/g/data/tm70/cyb561/access-om3-paper-1/notebooks/mkfigs_output_MC_25km_jra_iaf-1.0-beta-5165c0f8/mkmd/
DEST_PAGES=/home/561/cyb561/repos/access-om3-paper-1/documentation/docs/pages/
DEST_ASS=/home/561/cyb561/repos/access-om3-paper-1/documentation/docs/assets/experiments/

cp $OFOL/*.md $DEST_PAGES/index.md

mkdir -p ${DEST_ASS}${ENAME}

cp $OFOL*.png  ${DEST_ASS}${ENAME}/
