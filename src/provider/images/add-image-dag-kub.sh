#!/bin/bash

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
export nui

nui "send-to-database"
nui "extract-feature" 
nui "api-sys-reco-projet-ds"