"use strict";

const input_dir = 'cp2k_basis_webservice/assets/';
const output_dir = 'cp2k_basis_webservice/static/';

const tasks = [
    'grunt-contrib-jshint',
    'grunt-contrib-less',
    'grunt-contrib-uglify',
    'grunt-contrib-watch',
    'grunt-contrib-imagemin',
];

module.exports = function(grunt) {
    grunt.initConfig({
        jshint: {
            files: [`${input_dir}/*.js`],
            options: {
                jshintrc: true,
            }
        },
        less: {
            build: {
                options: {
                    compress: true
                },
                cwd: input_dir,
                src: [`*.less`],
                expand: true,
                dest: output_dir,
                ext: '.css'
            }
        },
        uglify: {
            build_script: {
                src: `${input_dir}/scripts.js`,
                dest: `${output_dir}/scripts.min.js`
            }
        },
        imagemin: {
            build: {
                files: [{
                    expand: true,
                    cwd: `${input_dir}/images`,
                    src: ['*.{png,svg}'],
                    dest: `${output_dir}/images`
                }]
            }
        },
        watch: {
            js: {
                files: ['<%= jshint.files %>'],
                tasks: ['jshint', 'uglify']
            },
            css: {
                files: ['<%= less.src %>'],
                tasks: ['less']
            }
        }
    });

    tasks.forEach((task) => {grunt.loadNpmTasks(task); });
    grunt.registerTask('default', ['jshint', 'less', 'uglify', 'imagemin']);
    grunt.registerTask('watch', ['watch']);
};