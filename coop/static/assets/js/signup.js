$(function ()
    {
        $("#signupForm").children("fieldset")
            .steps({
                headerTag: "h2",
                bodyTag: "section",
                transitionEffect: "slideLeft",
                enableFinishButton: true,
                stepsOrientation: "vertical",
                saveState: true,
                // Triggered when clicking the Previous/Next buttons
                onStepChanging: function(e, currentIndex, newIndex) {
                    var fv         = $('#signupForm').data('formValidation'), // FormValidation instance
                        // The current step container
                        $container = $('#signupForm').find('section[data-step="' + currentIndex +'"]');

                    // Validate the container
                    fv.validateContainer($container);

                    var isValidStep = fv.isValidContainer($container);
                    if (isValidStep === false || isValidStep === null) {
                        // Do not jump to the next step
                        return false;
                    }

                    return true;
                },
            })
            .formValidation({
                framework: 'bootstrap',
                icon: {
                    valid: 'bi bi-check',
                    invalid: 'bi bi-x',
                    validating: 'bi bi-bootstrap-reboot'
                },
                // This option will not ignore invisible fields which belong to inactive panels
                excluded: ':disabled',
                fields: {
                    phone: {
                        validators: {
                            notEmpty: {
                                message: 'The username is required'
                            },
                            stringLength: {
                                min: 6,
                                max: 30,
                                message: 'The username must be more than 6 and less than 30 characters long'
                            },
                            regexp: {
                                regexp: /^[0-9]+$/,
                                message: 'The username can only consist of alphabetical, number, dot and underscore'
                            }
                        }
                    },
                    email: {
                        validators: {
                            notEmpty: {
                                message: 'The email address is required'
                            },
                            emailAddress: {
                                message: 'The input is not a valid email address'
                            }
                        }
                    },
                    password1: {
                        validators: {
                            notEmpty: {
                                message: 'The password is required'
                            },
                            different: {
                                field: 'username',
                                message: 'The password cannot be the same as username'
                            }
                        }
                    },
                    password2: {
                        validators: {
                            notEmpty: {
                                message: 'The confirm password is required'
                            },
                            identical: {
                                field: 'password',
                                message: 'The confirm password must be the same as original one'
                            }
                        }
                    },
                    first_name: {
                        row: '.col-xs-4',
                        validators: {
                            notEmpty: {
                                message: 'The first name is required'
                            },
                            regexp: {
                                regexp: /^[a-zA-Z\s]+$/,
                                message: 'The first name can only consist of alphabetical and space'
                            }
                        }
                    },
                    middle_name: {
                        row: '.col-xs-4',
                        validators: {
                            notEmpty: {
                                message: 'The first name is required'
                            },
                            regexp: {
                                regexp: /^[a-zA-Z\s]+$/,
                                message: 'The first name can only consist of alphabetical and space'
                            }
                        }
                    },
                    last_name: {
                        row: '.col-xs-4',
                        validators: {
                            notEmpty: {
                                message: 'The last name is required'
                            },
                            regexp: {
                                regexp: /^[a-zA-Z\s]+$/,
                                message: 'The last name can only consist of alphabetical and space'
                            }
                        }
                    },
                    gender: {
                        validators: {
                            notEmpty: {
                                message: 'The gender is required'
                            }
                        }
                    },
                    date_of_birth: {
                        validators: {
                            notEmpty: {
                                message: 'The birthday is required'
                            },
                            date: {
                                format: 'YYYY/MM/DD',
                                message: 'The birthday is not valid'
                            }
                        }
                    },
                    bio: {
                        validators: {
                            stringLength: {
                                max: 200,
                                message: 'The bio must be less than 200 characters'
                            }
                        }
                    }
                }
         });
    });

//$(function(){
//    $("#example-basic").steps({
//        headerTag: "h2",
//        bodyTag: "section",
//        transitionEffect: "fade",
//        enableAllSteps: true,
//        stepsOrientation: "vertical",
//        autoFocus: true,
//        transitionEffectSpeed: 500,
//        titleTemplate : '<div class="title">#title#</div>',
//        labels: {
//            previous : 'Back Step',
//            next : '<i class="zmdi zmdi-arrow-right"></i>',
//            finish : '<i class="zmdi zmdi-check"></i>',
//            current : ''
//        },
//    })
//});


//$("#example-basic").steps({
//    headerTag: "h3",
//    bodyTag: "section",
//    transitionEffect: "slideLeft",
//    autoFocus: true
//});