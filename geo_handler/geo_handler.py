# -*- coding: utf-8 -*-
import geocoder

def addr2latlng(address):
    g = geocoder.google(address)
    return( g.latlng )
