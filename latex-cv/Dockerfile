FROM texlive/texlive

#RUN cd infographics2/fr/
#RUN ls -la

#WORKDIR infographics2/fr

RUN mkdir /tools

COPY build_cv.sh /tools/

CMD ["bash", "/tools/build_cv.sh"] 
