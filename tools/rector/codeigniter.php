<?php
use Rector\Config\RectorConfig;
use Rector\Transform\Rector\MethodCall\MethodCallRector;
use Rector\Transform\ValueObject\MethodCallRename;

return static function (RectorConfig $rectorConfig): void {
    // Règles pour migrer CodeIgniter 3 vers CodeIgniter 4
    $rectorConfig->sets([\Rector\CodeIgniter\Set\CodeIgniterLevelSetList::UP_TO_CODEIGNITER_4]);

    // Règle pour migrer les helpers (ex. : form_open)
    $rectorConfig->ruleWithConfiguration(
        MethodCallRector::class,
        [
            new MethodCallRename(
                'CI_Controller',
                'load->helper',
                '\CodeIgniter\CodeIgniter::helper'
            ),
        ]
    );

    // Règle pour migrer les sessions (ex. : $this->session->set_userdata vers session()->set)
    $rectorConfig->ruleWithConfiguration(
        MethodCallRector::class,
        [
            new MethodCallRename(
                'CI_Session',
                'set_userdata',
                '\CodeIgniter\Session\Session::set'
            ),
            new MethodCallRename(
                'CI_Session',
                'userdata',
                '\CodeIgniter\Session\Session::get'
            ),
        ]
    );

    // Chemins à analyser
    $rectorConfig->paths([__DIR__ . '/../../backend/app']);
};