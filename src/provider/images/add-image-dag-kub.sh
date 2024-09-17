#!/bin/bash

nui () 
{

    username=$(docker info | sed '/Username:/!d;s/.* //'); 
    echo "Prepare to upload image on docker hub. Your username is:\n";
    echo $username
    docker build -t $1 .;
    docker tag $1 $username/$2;
    docker push $username/$2;
    echo "$username/$2";
}
export nui

nui "send-to-database" "send-to-database"
nui "extract-feature" "extract-feature"