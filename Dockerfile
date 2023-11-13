FROM jupyter/datascience-notebook:ubuntu-20.04

# Install programs
USER root
RUN apt-get update
RUN apt-get install -y --force-yes libgeos++-dev libgeos-3.8.0 libgeos-c1v5 libgeos-dev libgeos-doc proj-bin vim git sudo gnupg mongodb mongodb-server lsof

# Install mongodb https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/
RUN echo "mongodb-org hold" | sudo dpkg --set-selections
RUN echo "mongodb-org-database hold" | sudo dpkg --set-selections
RUN echo "mongodb-org-server hold" | sudo dpkg --set-selections
RUN echo "mongodb-mongosh hold" | sudo dpkg --set-selections
RUN echo "mongodb-org-mongos hold" | sudo dpkg --set-selections
RUN echo "mongodb-org-tools hold" | sudo dpkg --set-selections

USER jovyan

# Install js modules
RUN npm install --save epoch gulp del gulp-htmlmin gulp-sass gulp-sourcemaps vinyl-source-stream vinyl-buffer gulp-uglify browserify browser-sync connect-history-api-fallback connect jquery gulp-shell node-cron tablesorter
RUN npm install --global gulp-cli http-server
RUN npm install -g gulp@v4 fix-esm

# Install python modules
RUN conda install -c anaconda line_profiler
RUN conda install tqdm xlsxwriter black pymongo flask openpyxl nodejs ipympl sqlalchemy snowflake-sqlalchemy

# Ensure notebook plotting works in jupyterlab
RUN jupyter lab build

# Set up github config including GITHUB TOKEN (get from github.com).
COPY .gitconfig ./
