//'use strict';

var gulp = require('gulp');
var del = require('del');
var htmlmin = require('gulp-htmlmin');
const sass = require('gulp-sass')(require('sass'));
var sourcemaps = require('gulp-sourcemaps');
var source = require('vinyl-source-stream');
var buffer = require('vinyl-buffer');
var uglify = require('gulp-uglify');
var browserify = require('browserify');
var browserSync = require('browser-sync').create();
var history = require('connect-history-api-fallback');
var connect = require('connect');
var jquery = require('jquery');
var shell = require('gulp-shell');
var cron = require('node-cron');
var exec = require('child_process').exec;
var spawn = require('child_process').spawn;
var exec = require('child_process').exec;
var spawnSync = require('child_process').spawnSync;
var shell = require('gulp-shell');

var app = connect()
  .use(history())
  .listen(5003);

const BUILD_DEST = "./build";
const STATIC_DEST = "/static";
//CLEAN
gulp.task('clean:html', function (done) {
    return del([BUILD_DEST + "/html/*"], done());
});

gulp.task('clean:js', function (done) {
//  return del([BUILD_DEST + "/js/*"], done());
  return del([BUILD_DEST + STATIC_DEST + "/*.js"], done());
});

gulp.task('clean:css', function (done) {
//    return del([BUILD_DEST + "/css/*"], done());
    return del([BUILD_DEST + STATIC_DEST + "/*.css"], done());
});

gulp.task('clean:py', function (done) {
      return del([BUILD_DEST + "/py/*"], done());
});

gulp.task('clean:resources', function (done) {
  return del([BUILD_DEST + STATIC_DEST + "/resources/*"], done());
});

gulp.task('clean', gulp.parallel('clean:py', 'clean:js', 'clean:css', 'clean:html','clean:resources'));


//BUILD
gulp.task('build:html', function (done) {
    return gulp.src('./src/html/*.html')
        .pipe(htmlmin({collapseWhitespace: true}))
        .pipe(gulp.dest(BUILD_DEST+'/html/')),
      done();
});

gulp.task('build:js', function (done) {
    // set up the browserify instance on a task basis
    var b = browserify({
        entries: ['./src/js/main.js']
    });

    return b.bundle()
        .pipe(source('app.min.js'))
        .pipe(buffer())
        .pipe(sourcemaps.init({loadMaps: true}))
        // Add transformation tasks to the pipeline here.
//        .pipe(uglify())       //minify
        .pipe(sourcemaps.write('./'))
        .pipe(gulp.dest(BUILD_DEST+STATIC_DEST)),
        done();
});

gulp.task('build:css', function (done) {
    return gulp.src('./src/sass/*')
        .pipe(sass({outputStyle: 'compressed'}))
        .pipe(gulp.dest(BUILD_DEST+STATIC_DEST)),
        done();
});

gulp.task('build:py', function (done) {
    return gulp.src('./src/py/*.py')
        .pipe(gulp.dest(BUILD_DEST+'/py/')),
      done();
});

gulp.task('build:resources', function (done) {
  return gulp.src('./src/resources/**/*.*')
      .pipe(gulp.dest(BUILD_DEST+STATIC_DEST+'/resources/')),
    done();
});

gulp.task('build', gulp.parallel('build:py', 'build:css', 'build:js', 'build:html','build:resources'));


//Python server
gulp.task('flask', function(done) {
    spawn('bash', ['_server_initiate.sh'], { stdio: 'inherit' })
    done();
});


//WATCH
gulp.task('watch:html', function() {
  gulp.watch('./src/html/**/*', {interval: 1000, usePolling: true}, gulp.series('clean:html', 'build:html', 'flask')).on('change', browserSync.reload);
});
gulp.task('watch:css', function() {
    gulp.watch('./src/sass/**/*', {interval: 1000, usePolling: true}, gulp.series('clean:css', 'build:css')).on('change', browserSync.reload);
});
gulp.task('watch:js', function() {
    gulp.watch('./src/js/**/*', {interval: 1000, usePolling: true}, gulp.series('clean:js', 'build:js')).on('change', browserSync.reload);
});
gulp.task('watch:py', function() {
    gulp.watch('./src/py/**/*', {interval: 1000, usePolling: true}, gulp.series('clean:py', 'build:py', 'flask')).on('change', browserSync.reload);
});
gulp.task('watch:resources', function() {
  gulp.watch('./src/resources/**/*', {interval: 1000, usePolling: true}, gulp.series('clean:resources', 'build:resources')).on('change', browserSync.reload);
});

gulp.task('watch', gulp.parallel('watch:html', 'watch:js', 'watch:css', 'watch:py','watch:resources'));


//SERVE
gulp.task('serve', gulp.series('clean', 'build', 'flask', 'watch', function() {
  browserSync.init({
    server: {
      baseDir: BUILD_DEST
    },
    reloadDelay: 1000
  })
}));


//DEFAULT
gulp.task('default', function () {
    console.log('Useage is as follows with one or more of the configured tasks:\n' +
        '$ gulp <task> [<task2> ...] \n' +
        'available options:\n' +
        '\t* clean - cleans the built project\n' +
        '\t\t-clean:html - cleans just the html\n' +
        '\t\t-clean:css - cleans just the css\n' +
        '\t\t-clean:js - cleans just the js\n' +
        '\t* build - build the entire project\n' +
        '\t\t-build:html - builds just the html\n' +
        '\t\t-build:css - builds just the css\n' +
        '\t\t-build:js - builds just the js\n' +
        '\t* serve - cleans, builds and serves the project watching for any changes\n');
});
