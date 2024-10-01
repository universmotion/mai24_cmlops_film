nui () 
{
    username=$(docker info | sed '/Username:/!d;s/.* //'); 
    echo "Prepare to upload image on docker hub. Your username is:\n";
    echo $username
    docker build -t $1 $2;
    docker tag $1 $username/$1;
    docker push $username/$1;
    echo "$username/$1";
}

# nui "train-model" src/provider/images/train_model ;
# nui "send-to-database" src/provider/images/send_to_database ;
# nui "extract-feature" src/provider/images/extract_feature ;
# nui "scraping-data" src/provider/images/scraping_data ;
nui "api-sys-reco-projet-ds" src/API ;