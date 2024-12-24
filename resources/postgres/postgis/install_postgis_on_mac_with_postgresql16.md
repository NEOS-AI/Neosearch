# Install PostGIS on Mac with PostgreSQL 16

```bash
# Need to remove existing postgis and must not have postgresql@14 present
[brew remove postgis]
[brew remove postgresql@14]

# reinstall json-c once above are removed
brew uninstall json-c
brew install json-c
brew link json-c

# install postgresql@16 if not already installed - check version specific path
brew install postgresql@16
sudo ln -sf /opt/homebrew/Cellar/postgresql@16/16.4/bin/postgres /usr/local/bin/postgres
sudo chown -R "$USER":admin /usr/local/bin /usr/local/share

# utilities if you need them installed
brew install wget
brew install pcre

# if you get errors not finding `libintl.h` 
brew reinstall gettext
brew unlink gettext && brew link gettext --force

# install postgis dependencies
brew install geos gdal libxml2 sfcgal protobuf-c

# build postgis from source
wget https://download.osgeo.org/postgis/source/postgis-3.4.2.tar.gz
tar -xvzf postgis-3.4.2.tar.gz
rm postgis-3.4.2.tar.gz
cd postgis-3.4.2

./configure --with-projdir=/opt/homebrew/opt/proj --with-pgconfig=/opt/homebrew/opt/postgresql@16/bin/pg_config --with-jsondir=/opt/homebrew/opt/json-c --with-sfcgal=/opt/homebrew/opt/sfcgal/bin/sfcgal-config --with-pcredir=/opt/homebrew/opt/pcre --without-protobuf --without-topology "LDFLAGS=$LDFLAGS -L/opt/homebrew/Cellar/gettext/0.22.5/lib" "CFLAGS=-I/opt/homebrew/Cellar/gettext/0.22.5/include" 

# build/make
make
make install


##############################################################
Alternative config that worked in the past but did not for me
##############################################################

# check gettext version specific path
# - not working, gives protobuf error
# ./configure --with-projdir=/opt/homebrew/opt/proj --with-protobufdir=/opt/homebrew/opt/protobuf-c --with-pgconfig=/opt/homebrew/opt/postgresql@16/bin/pg_config --with-jsondir=/opt/homebrew --with-sfcgal=/opt/homebrew/opt/sfcgal/bin/sfcgal-config --with-pcredir=/opt/homebrew/opt/pcre "LDFLAGS=$LDFLAGS -L/opt/homebrew/Cellar/gettext/0.22.5/lib" "CFLAGS=-I/opt/homebrew/Cellar/gettext/0.22.5/include"

# alternative 
# ./configure --with-projdir=/opt/homebrew/opt/proj --with-pgconfig=/opt/homebrew/opt/postgresql@16/bin/pg_config --with-jsondir=/opt/homebrew --with-sfcgal=/opt/homebrew/opt/sfcgal/bin/sfcgal-config --with-pcredir=/opt/homebrew/opt/pcre --without-protobuf --without-topology "LDFLAGS=$LDFLAGS -L/opt/homebrew/Cellar/gettext/0.22.5/lib" "CFLAGS=-I/opt/homebrew/Cellar/gettext/0.22.5/include"

# build/make
[sudo] [NO_GETTEXT=1] make
[sudo] [NO_GETTEXT=1] make install
```
