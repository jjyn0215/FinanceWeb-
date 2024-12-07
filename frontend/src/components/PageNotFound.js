import React, { Component, useEffect } from 'react';
import { enqueueSnackbar, closeSnackbar } from "notistack";


export default function PageNotFound(){
    useEffect(() => {
        closeSnackbar('offline');
    });

    return (
        <h1>
            404 PAGE NOT FOUND
        </h1>

    )
}